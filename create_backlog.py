import os
import sys
import time
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, field

from jira import JIRA
from dotenv import load_dotenv, find_dotenv

# ---------- Config & Auth ----------
load_dotenv(find_dotenv())

BASE  = (os.getenv("JIRA_BASE") or "").rstrip("/")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")
PROJ  = (os.getenv("JIRA_PROJECT_KEYS") or "WEAT").split(",")[0].strip()

if not (BASE and EMAIL and TOKEN and PROJ):
    print("❌ Missing one or more env vars: JIRA_BASE, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEYS")
    sys.exit(1)

jira = JIRA(server=BASE, basic_auth=(EMAIL, TOKEN))
print(f"✅ Authenticated as {jira.current_user()} on {BASE}, project={PROJ}")

# ---------- Utilities ----------
def find_field_id_by_name(name_contains: str) -> Optional[str]:
    """
    Search Jira fields for one whose name contains the given substring (case-insensitive).
    Returns the field id, e.g. 'customfield_10014' for 'Epic Link', if found.
    """
    for f in jira.fields():
        try:
            if name_contains.lower() in f["name"].lower():
                return f["id"]
        except Exception:
            continue
    return None

def project_uses_company_managed_epic_link() -> Tuple[bool, Optional[str]]:
    """
    Detect whether the site exposes a classic 'Epic Link' custom field (company-managed).
    Returns (True, field_id) if found; else (False, None) for likely team-managed epic parenting.
    """
    epic_link_id = find_field_id_by_name("Epic Link")
    return (epic_link_id is not None, epic_link_id)

def search_issue_by_summary(project: str, summary: str) -> Optional[str]:
    """
    Idempotency: look for an existing issue with the exact summary in this project.
    Returns the issue key if found.
    """
    # Use a quoted contains-search, then exact-compare client-side
    jql = f'project = "{project}" AND summary ~ "\\"{summary}\\"" ORDER BY created DESC'
    try:
        res = jira.search_issues(jql, maxResults=10, fields="summary")
    except Exception:
        return None
    for issue in res:
        if (getattr(issue.fields, "summary", "") or "").strip().lower() == summary.strip().lower():
            return issue.key
    return None

def resolve_types_for_project(project_key: str) -> Dict[str, Optional[Dict[str, str]]]:
    """
    Returns a dict of {'epic': {'id': ...}, 'task': {'id': ...}, 'subtask': {'id': ... or None}}
    using the issue types actually available in this project.
    """
    proj = jira.project(project_key)
    # Prefer the dedicated helper when available (Jira Cloud)
    try:
        types = jira.issue_types_for_project(proj.id)
    except Exception:
        types = getattr(proj, "issueTypes", []) or []

    by_lower = {t.name.lower(): t for t in types if getattr(t, "name", None)}

    def get_id(*names):
        for n in names:
            t = by_lower.get(n.lower())
            if t:
                return {"id": t.id}
        return None

    epic    = get_id("Epic")
    # Many team-managed projects use "Story" instead of "Task" as the standard work item
    task    = get_id("Task", "Story", "Bug")
    subtask = get_id("Sub-task", "Subtask")  # some TM projects display “Subtask” (no hyphen)

    if not epic:
        raise RuntimeError(f"Issue type 'Epic' not available in {project_key}. "
                           f"Add it in Project settings → Issue types.")
    if not task:
        raise RuntimeError(f"No suitable 'Task' or 'Story' issue type in {project_key}. "
                           f"Add one in Project settings.")

    return {"epic": epic, "task": task, "subtask": subtask}

TYPES = resolve_types_for_project(PROJ)
print("🧩 Issue type IDs:", {k: v and v.get("id") for k, v in TYPES.items()})

# Company-managed vs team-managed parenting
IS_COMPANY, EPIC_LINK_FIELD = project_uses_company_managed_epic_link()
print(f"ℹ️ Epic linking mode: {'company-managed via ' + EPIC_LINK_FIELD if IS_COMPANY else 'team-managed (parent)'}")

def _massage_issue_fields_for_types(fields: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Convert {'issuetype': {'name': 'Epic/Task/Sub-task'}} into ID-based fields for the current project.
    If 'Sub-task' is not available, fall back to Task:
      - remove 'parent'
      - add label 'subtask-fallback'
      - prefix summary '[Subtask] '
      - return the original parent key so we can link after creation
    Returns (new_fields, fallback_parent_key_if_any)
    """
    new_fields = dict(fields)  # shallow copy
    issuetype = (new_fields.get("issuetype") or {})
    requested_name = (issuetype.get("name") or "").strip().lower()

    fallback_parent_key = None

    if requested_name == "epic":
        new_fields["issuetype"] = TYPES["epic"]

    elif requested_name == "task":
        new_fields["issuetype"] = TYPES["task"]

    elif requested_name in ("sub-task", "subtask"):
        if TYPES["subtask"] is not None:
            new_fields["issuetype"] = TYPES["subtask"]
        else:
            # Fallback: create as Task/Story, not as subtask
            parent = new_fields.pop("parent", None)
            if parent and isinstance(parent, dict):
                fallback_parent_key = parent.get("key")
            new_fields["issuetype"] = TYPES["task"]
            # Label + summary note
            labels = list(new_fields.get("labels") or [])
            if "subtask-fallback" not in labels:
                labels.append("subtask-fallback")
            new_fields["labels"] = labels
            # Prefix summary to make it obvious
            s = (new_fields.get("summary") or "").strip()
            if not s.startswith("[Subtask] "):
                new_fields["summary"] = f"[Subtask] {s}"
    else:
        # If name not provided, leave as-is (caller may already pass an id)
        pass

    return new_fields, fallback_parent_key

def create_issue_with_retry(fields: dict, retries: int = 3):
    """
    Creates an issue but normalizes issue type to project-specific IDs.
    Also handles sub-task fallback (creates a Task and links back to the parent Task).
    """
    prepared_fields, fallback_parent_key = _massage_issue_fields_for_types(fields)

    last_exc = None
    for i in range(retries):
        try:
            issue = jira.create_issue(fields=prepared_fields)
            # If we fell back from sub-task → task, relate it to the parent Task for traceability
            if fallback_parent_key:
                try:
                    jira.create_issue_link(type="Relates",
                                           inwardIssue=issue.key,
                                           outwardIssue=fallback_parent_key)
                except Exception:
                    # Non-fatal
                    pass
            return issue
        except Exception as e:
            last_exc = e
            if i < retries - 1:
                time.sleep(1.5)
            else:
                raise last_exc

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Subtask:
    summary: str
    description: str
    labels: List[str] = field(default_factory=list)
    priority: Optional[str] = None

@dataclass
class Task:
    summary: str
    description: str
    labels: List[str] = field(default_factory=list)
    priority: Optional[str] = "Medium"
    subtasks: List[Subtask] = field(default_factory=list)

@dataclass
class Epic:
    summary: str
    description: str
    labels: List[str] = field(default_factory=lambda: ["roadmap"])
    priority: Optional[str] = "High"
    tasks: List[Task] = field(default_factory=list)

# ---------- BACKLOG DEFINITION ----------
def get_backlog() -> List[Epic]:
    return [

        # 🌤 Epic 1
        Epic(
            summary="WeatherDashboard v2 (Frontend)",
            labels=["frontend","react","dashboard","roadmap"],
            description=(
                "Goal: Build a modular, high-performance React interface that visualizes weather, wind, and radar data "
                "from the unified backend, blending aesthetic excellence with purpose-driven craftsmanship."
            ),
            tasks=[

                Task(
                    summary="Port WeatherDashboard to React v2 Shell",
                    labels=["frontend","react","routing"],
                    description="Rebuild the shell with Layout/Navbar, 3 pages, Router v6, Axios, responsive grid, and Vercel deploy.",
                    subtasks=[
                        Subtask(
                            summary="Create Layout.js and Navbar.js reusable components",
                            labels=["frontend","ui","react"],
                            description=(
                                "*Summary*\n"
                                "Establish the visual and structural foundation of the application with shared layout and navigation components.\n\n"
                                "*Detailed Work*\n"
                                "Create `Layout.js` to wrap the app (header/footer/content) with responsive breakpoints and centered content. "
                                "Implement `Navbar.js` using shadcn/ui or Tailwind with links for Dashboard, Results, and About. "
                                "Use React Router v6 `<NavLink>` for active styles and add a Framer-Motion mobile menu. "
                                "Smoke-test with placeholder pages across routes.\n\n"
                                "*Faith Integration*\n"
                                "Direct my footsteps according to your word; let no sin rule over me..\n\n"
                                "*Resources*\n"
                                "- React Router layout patterns\n- shadcn/ui navbar example\n- Tailwind responsive guide"
                            )
                        ),
                        Subtask(
                            summary="Implement 3 primary pages: WeatherDashboard, Results, About",
                            labels=["frontend","routing"],
                            description=(
                                "*Summary*\nDefine and route the main pages, ensuring modularity.\n\n"
                                "*Detailed Work*\n"
                                "Create `src/pages/WeatherDashboard.js`, `Results.js`, `About.js`. Wire with `<Routes>` in `App.js`. "
                                "Add lazy loading with `React.lazy`/`Suspense`. WeatherDashboard gets slots for charts/selectors/summaries; "
                                "Results will host roadmap tabs; About shows mission statement.\n\n"
                                "*Faith Integration*\n"
                                "By wisdom a house is built, and through understanding it is established; through knowledge its rooms are filled with rare and beautiful treasures..\n\n"
                                "*Resources*\n"
                                "- React Router routes\n- React Suspense"
                            )
                        ),
                        Subtask(
                            summary="Add React Router for tab navigation",
                            labels=["frontend","routing"],
                            description=(
                                "*Summary*\nEnable dynamic navigation with Router v6.\n\n"
                                "*Detailed Work*\n"
                                "`npm i react-router-dom`. Configure `<BrowserRouter>` and `<Routes>`. Use `<NavLink>` for active states. "
                                "Lazy-import page components. Verify desktop/mobile flows.\n\n"
                                "*Faith Integration*\n"
                                "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight.\n\n"
                                "*Resources*\n"
                                "- React Router docs\n- WDS v6 tutorial"
                            )
                        ),
                        Subtask(
                            summary="Integrate Axios base URL via .env",
                            labels=["frontend","api"],
                            description=(
                                "*Summary*\nConnect frontend to backend via env config.\n\n"
                                "*Detailed Work*\n"
                                "Install Axios; create `apiClient.js` with `baseURL=process.env.REACT_APP_API_BASE_URL`. "
                                "Add interceptors for errors/offline fallback. Configure `.env.*` for dev/prod Vercel.\n\n"
                                "*Faith Integration*\n"
                                "'I am the vine; you are the branches. If you remain in me and I in you, you will bear much fruit; apart from me you can do nothing.' \n\n"
                                "*Resources*\n"
                                "- Axios docs\n- Vercel env vars guide"
                            )
                        ),
                        Subtask(
                            summary="Add responsive CSS grid layout",
                            labels=["frontend","ui"],
                            description=(
                                "*Summary*\nCreate an adaptive grid using Tailwind.\n\n"
                                "*Detailed Work*\n"
                                "Use `grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 p-4`. "
                                "Implement card sizing for charts/summaries/controls; test in DevTools; keep palette minimal.\n\n"
                                "*Faith Integration*\n"
                                "To the weak I became weak, to win the weak. I have become all things to all people so that by all possible means I might save some.\n\n"
                                "*Resources*\n"
                                "- Tailwind grid\n- CSS-Tricks responsive grids"
                            )
                        ),
                        Subtask(
                            summary="Test build on Vercel with .env.production",
                            labels=["frontend","deploy"],
                            description=(
                                "*Summary*\nDeploy and validate prod settings.\n\n"
                                "*Detailed Work*\n"
                                "Link GitHub→Vercel, set env vars, deploy preview → prod. Verify API calls, routes, Lighthouse/a11y; "
                                "fix CORS/404 if any.\n\n"
                                "*Faith Integration*\n"
                                "The plans of the diligent lead to profit as surely as haste leads to poverty.\n\n"
                                "*Resources*\n"
                                "- Vercel React deploy\n- Lighthouse"
                            )
                        ),
                    ]
                ),

                Task(
                    summary="Time-Series Wind Chart with Directional Arrows",
                    labels=["frontend","charts","wind"],
                    description="Reusable wind time-series chart with direction glyphs, unit toggles, tooltips, and golden tests.",
                    subtasks=[
                        Subtask(
                            summary="Fetch /api/graph_data?metric=wind_speed_avg",
                            labels=["frontend","api"],
                            description=(
                                "*Summary*\nConnect to hourly wind time-series.\n\n"
                                "*Detailed Work*\n"
                                "Fetch `/api/graph_data?metric=wind_speed_avg&station_id=...&period=...`. "
                                "Store in state; handle empty/delayed responses gracefully.\n\n"
                                "*Faith Integration*\n"
                                "Data integrity and trust.\n\n"
                                "*Resources*\n"
                                "- Axios async fetching\n- MDN Promise.all"
                            )
                        ),
                        Subtask(
                            summary="Build <WindLineChart /> component",
                            labels=["frontend","charts"],
                            description=(
                                "*Summary*\nComposable chart with zoom/brush.\n\n"
                                "*Detailed Work*\n"
                                "Use Recharts (LineChart, Tooltip, Brush) or D3; normalize time; decimate dense series; expose `onRangeChange`.\n\n"
                                "*Faith Integration*\n"
                                "Commit to the Lord whatever you do, and he will establish your plans.\n\n"
                                "*Resources*\n"
                                "- Recharts LineChart\n- D3 line chart"
                            )
                        ),
                        Subtask(
                            summary="Overlay directional arrows (rotation by degrees)",
                            labels=["frontend","charts","svg"],
                            description=(
                                "*Summary*\nShow wind direction as rotated glyphs.\n\n"
                                "*Detailed Work*\n"
                                "Add small SVG arrows per sample rotated by `wind_dir_deg` (0–360). "
                                "Color by speed; decimate at high density; provide legend.\n\n"
                                "*Faith Integration*\n"
                                "Whatever you do, work at it with all your heart, as working for the Lord, not for human masters,\n\n"
                                "*Resources*\n"
                                "- SVG transform attr\n- Recharts custom dot"
                            )
                        ),
                        Subtask(
                            summary="Toggle sustained vs gust & unit switching",
                            labels=["frontend","ui"],
                            description=(
                                "*Summary*\nSegmented metric and unit toggles.\n\n"
                                "*Detailed Work*\n"
                                "Toggle wind_speed_avg vs wind_gust_max; units m/s|kt|mph; persist preference; "
                                "update axis/legend/tooltip accordingly.\n\n"
                                "*Faith Integration*\n"
                                "If any of you lacks wisdom, you should ask God, who gives generously to all without finding fault, and it will be given to you. \n\n"
                                "*Resources*\n"
                                "- shadcn/ui Toggle\n- WMO unit refs"
                            )
                        ),
                        Subtask(
                            summary="Rich tooltip (station/time/dir/speed)",
                            labels=["frontend","ui","a11y"],
                            description=(
                                "*Summary*\nContextual details + accessibility.\n\n"
                                "*Detailed Work*\n"
                                "Custom tooltip with ISO time (UTC/local), station, sustained/gust, deg+cardinal; "
                                "keyboard focus and pin mode.\n\n"
                                "*Faith Integration*\n"
                                "The heart of the discerning acquires knowledge, for the ears of the wise seek it out.\n\n"
                                "*Resources*\n"
                                "- Recharts custom tooltip\n- date-fns-tz"
                            )
                        ),
                        Subtask(
                            summary="Validate against hourly API (golden + visual)",
                            labels=["frontend","tests"],
                            description=(
                                "*Summary*\nGolden fixture + Storybook.\n\n"
                                "*Detailed Work*\n"
                                "Golden dataset; Storybook stories; optional visual regression; verify wrap boundaries and unit toggles.\n\n"
                                "*Faith Integration*\n"
                                "but test them all; hold on to what is good, \n\n"
                                "*Resources*\n"
                                "- Storybook\n- Chromatic"
                            )
                        ),
                    ]
                ),

                Task(
                    summary="24-Clock Wind-Rose Small Multiples",
                    labels=["frontend","charts","wind-rose"],
                    description="Polar histograms for 24 hours; radius=freq, color=median speed; wrap QA & exports.",
                    subtasks=[
                        Subtask(
                            summary="Design <WindRose /> (bins & radius scaling)",
                            labels=["frontend","charts"],
                            description=(
                                "*Summary*\nPolar histogram component.\n\n"
                                "*Detailed Work*\n"
                                "Bin by 10°; draw sectors with d3.arc; sqrt radius; legends; props for bins/radiusMax/colorBy.\n\n"
                                "*Faith Integration*\n"
                                "The Lord detests dishonest scales, but accurate weights find favor with him.\n\n"
                                "*Resources*\n"
                                "- d3-shape arc\n- Wind rose refs"
                            )
                        ),
                        Subtask(
                            summary="Grid of 24 roses (00–23h) with shared legends",
                            labels=["frontend","charts","ui"],
                            description=(
                                "*Summary*\nSmall-multiples grid.\n\n"
                                "*Detailed Work*\n"
                                "<WindRoseGrid> with shared scales; hour labels; hover enlarge; export PNG/SVG.\n\n"
                                "*Faith Integration*\n"
                                "There is a time for everything, and a season for every activity under the heavens:\n\n"
                                "*Resources*\n"
                                "- CSS Grid\n- saveSvgAsPng"
                            )
                        ),
                        Subtask(
                            summary="Compute frequency per bin; handle missing & calm winds",
                            labels=["frontend","charts","qa"],
                            description=(
                                "*Summary*\nRobust binning & wrap.\n\n"
                                "*Detailed Work*\n"
                                "Normalize [0,360); separate calm bin; ensure sum(bins)==N; unit tests with fixtures.\n\n"
                                "*Faith Integration*\n"
                                "'Whoever can be trusted with very little can also be trusted with much, and whoever is dishonest with very little will also be dishonest with much.'\n\n"
                                "*Resources*\n"
                                "- Circular stats intro"
                            )
                        ),
                        Subtask(
                            summary="Color by median speed; build legend & thresholds",
                            labels=["frontend","charts","ui"],
                            description=(
                                "*Summary*\nColor encodes intensity.\n\n"
                                "*Detailed Work*\n"
                                "Compute median speed per bin; map to ramp; legend with thresholds; persist choice.\n\n"
                                "*Faith Integration*\n"
                                "The beginning of wisdom is this: Get wisdom. Though it cost all you have, get understanding.\n\n"
                                "*Resources*\n"
                                "- d3-scale-chromatic\n- WCAG contrast"
                            )
                        ),
                        Subtask(
                            summary="Validate wrap-around & bin sums (QA hooks)",
                            labels=["frontend","qa","tests"],
                            description=(
                                "*Summary*\nAutomated QA checks.\n\n"
                                "*Detailed Work*\n"
                                "Expose `validateRose()`; warn on mismatches; surface QA badge; capture metrics to `/api/status`.\n\n"
                                "*Faith Integration*\n"
                                "'All you need to say is simply ‘Yes’ or ‘No’; anything beyond this comes from the evil one.'\n\n"
                                "*Resources*\n"
                                "- Client logging (MDN)"
                            )
                        ),
                        Subtask(
                            summary="Integrate into Wind Analysis section",
                            labels=["frontend","ui"],
                            description=(
                                "*Summary*\nCompose with time-series.\n\n"
                                "*Detailed Work*\n"
                                "Wind Analysis tab: time-series (top), rose grid (bottom). Sync brushed range; export CSV/PNG; light client analytics.\n\n"
                                "*Faith Integration*\n"
                                "From him the whole body, joined and held together by every supporting ligament, grows and builds itself up in love, as each part does its work."
                            )
                        ),
                    ]
                ),

                Task(
                    summary="MRMS Radar Overlay (NW + Hawaii)",
                    labels=["frontend","map","radar"],
                    description="Map with MRMS composites, opacity/time control, station icons, perf & a11y.",
                    subtasks=[
                        Subtask(
                            summary="Evaluate MRMS sources & tiling strategy",
                            labels=["map","radar"],
                            description=(
                                "*Summary*\nPick product & serving approach.\n\n"
                                "*Detailed Work*\n"
                                "Prototype with existing MRMS tiles; plan COG+titiler proxy later; document cadence/retention.\n\n"
                                "*Faith Integration*\n"
                                " 'Suppose one of you wants to build a tower. Won’t you first sit down and estimate the cost to see if you have enough money to complete it?'\n\n"
                                "*Resources*\n"
                                "- NOAA MRMS overview\n- titiler/COG"
                            )
                        ),
                        Subtask(
                            summary="Build Leaflet/MapLibre base map (NW + HI)",
                            labels=["map","frontend"],
                            description=(
                                "*Summary*\nMinimal, performant basemap.\n\n"
                                "*Detailed Work*\n"
                                "Init map, extent buttons for PNW/HI, scalebar/attribution, light basemap; check WebGL and cleanup.\n\n"
                                "*Faith Integration*\n"
                                "The boundary lines have fallen for me in pleasant places;\n\n"
                                "*Resources*\n"
                                "- MapLibre GL\n- Leaflet quickstart"
                            )
                        ),
                        Subtask(
                            summary="Overlay radar tiles with opacity & timestamp",
                            labels=["map","radar","ui"],
                            description=(
                                "*Summary*\nRaster layer + controls.\n\n"
                                "*Detailed Work*\n"
                                "Add toggle and opacity slider; show as-of time; poll modestly; cache last timestamp; degrade on staleness.\n\n"
                                "*Faith Integration*\n"
                                "Whoever obeys his command will come to no harm, and the wise heart will know the proper time and procedure. For there is a proper time and procedure for every matter, though a person may be weighed down by misery."
                            )
                        ),
                        Subtask(
                            summary="Stations & icons layer (buoy/airport/PWS)",
                            labels=["map","stations","ui"],
                            description=(
                                "*Summary*\nType-specific symbols + popovers.\n\n"
                                "*Detailed Work*\n"
                                "GeoJSON layer with buoy/plane/house icons; cluster low zoom; popovers show key metrics + freshness; filter by type.\n\n"
                                "*Faith Integration*\n"
                                "Be sure you know the condition of your flocks, give careful attention to your herds;"
                            )
                        ),
                        Subtask(
                            summary="Performance tuning (throttle, decimate, cache)",
                            labels=["performance","map"],
                            description=(
                                "*Summary*\nKeep interactions smooth.\n\n"
                                "*Detailed Work*\n"
                                "Throttle pan/zoom; decimate markers; cache GeoJSON with ETags; target >45 FPS.\n\n"
                                "*Faith Integration*\n"
                                "The one who has knowledge uses words with restraint, and whoever has understanding is even-tempered."
                            )
                        ),
                        Subtask(
                            summary="Legend, units, and accessibility",
                            labels=["a11y","ui","map"],
                            description=(
                                "*Summary*\nExplainers and accessible controls.\n\n"
                                "*Detailed Work*\n"
                                "dBZ legend, unit info, keyboardable toggles, ARIA, color-blind palette, good contrast.\n\n"
                                "*Faith Integration*\n"
                                "Each of us should please our neighbors for their good, to build them up. "
                            )
                        ),
                    ]
                ),

                Task(
                    summary="Results Page (3-Tab Roadmap Display)",
                    labels=["frontend","results","portfolio"],
                    description="Tabs for Eng/Infra, Analytics/Arch, AI/ML; bind to live status JSON; screenshots; Jira rollup; deploy.",
                    subtasks=[
                        Subtask(
                            summary="Implement tabs: Eng/Infra, Analytics/Arch, AI/ML",
                            labels=["frontend","ui"],
                            description=(
                                "*Summary*\nTabbed interface mirroring the three roadmaps.\n\n"
                                "*Detailed Work*\n"
                                "shadcn/ui Tabs with route param; lazy content; status chips and progress bars.\n\n"
                                "*Faith Integration*\n"
                                "But everything should be done in a fitting and orderly way."
                            )
                        ),
                        Subtask(
                            summary="Bind to live JSON status",
                            labels=["frontend","api"],
                            description=(
                                "*Summary*\nData-driven Results page.\n\n"
                                "*Detailed Work*\n"
                                "Fetch `/api/results_status` (or local JSON fallback); memoize; manual & auto refresh.\n\n"
                                "*Faith Integration*\n"
                                "Therefore each of you must put off falsehood and speak truthfully to your neighbor, for we are all members of one body."
                            )
                        ),
                        Subtask(
                            summary="Screenshots & proofs (gallery)",
                            labels=["frontend","ui"],
                            description=(
                                "*Summary*\nEvidence of progress.\n\n"
                                "*Detailed Work*\n"
                                "Lightbox gallery for PNG/SVG and PR/demo links; filters by epic/task; story view for walkthroughs.\n\n"
                                "*Faith Integration*\n"
                                "Then the Lord replied: “Write down the revelation and make it plain on tablets so that a herald may run with it."
                            )
                        ),
                        Subtask(
                            summary="Auto-summary from Jira (read-only)",
                            labels=["frontend","jira","api"],
                            description=(
                                "*Summary*\nCounts by label and status.\n\n"
                                "*Detailed Work*\n"
                                "Server or proxy endpoint to read Jira counts; cache 10m; link to KAN filters.\n\n"
                                "*Faith Integration*\n"
                                "As iron sharpens iron, so one person sharpens another."
                            )
                        ),
                        Subtask(
                            summary="Deploy to glasierdata.com/results & validate",
                            labels=["frontend","deploy"],
                            description=(
                                "*Summary*\nShip and verify.\n\n"
                                "*Detailed Work*\n"
                                "Vercel route; Lighthouse & a11y; link checks; ‘last updated’ with timezone.\n\n"
                                "*Faith Integration*\n"
                                "May the favor of the Lord our God rest on us; establish the work of our hands for us—yes, establish the work of our hands."
                            )
                        ),
                    ]
                ),
            ],
        ),

        # ⚙️ Epic 2
        Epic(
            summary="API & ETL v2 (Backend)",
            labels=["backend","etl","flask","roadmap"],
            description=(
                "Flask app factory + blueprints; stable /api/* contracts; Postgres models/migrations; ETL bronze→silver→gold; "
                "validation & caching; Render deploy + cron."
            ),
            tasks=[
                Task(
                    summary="Flask App Factory + Blueprints",
                    labels=["backend","flask","api"],
                    description="Refactor into create_app + blueprints; CORS/security headers; JSON logging; error handlers; pytestable endpoints.",
                    subtasks=[
                        Subtask(
                            summary="Restructure Flask with create_app() and Blueprints",
                            labels=["backend","flask"],
                            description=(
                                "Create `app/__init__.py` with `create_app`; register blueprints; move routes to `app/api/*`; add `wsgi.py` for Gunicorn."
                                "*Faith Integration*\n"
                                "The reason I left you in Crete was that you might put in order what was left unfinished and appoint elders in every town, as I directed you."
                            )
                        ),
                        Subtask(
                            summary="Define /api/summary_data, /api/graph_data, /api/status",
                            labels=["backend","api"],
                            description=(
                                "Implement handlers with validation; return JSON incl. granularity, units, station, window; add ETag/Cache-Control."
                                "*Faith Integration*\n"
                                "An honest witness tells the truth, but a false witness tells lies."
                            )
                        ),
                        Subtask(
                            summary="CORS for Vercel + security headers",
                            labels=["backend","security"],
                            description=(
                                "Configure flask-cors for allowed origins; add HSTS/nosniff/referrer-policy; verify preflights."
                                "Above all else, guard your heart, for everything you do flows from it."
                            )
                        ),
                        Subtask(
                            summary="Logging & error handling middleware",
                            labels=["backend","logging"],
                            description=(
                                "Request/response JSON logs with request_id; 400/404/422/500 handlers returning structured errors."
                                "*Faith Integration*\n"
                                "The Lord detests lying lips, but he delights in people who are trustworthy."
                            )
                        ),
                        Subtask(
                            summary="Pytest HTTP tests for endpoints",
                            labels=["tests","backend"],
                            description=(
                                "pytest + httpx/pytest-flask against `create_app('test')`; fixtures for temp DB; success/error cases; snapshots."
                                "*Faith Integration*\n"
                                "Do your best to present yourself to God as one approved, a worker who does not need to be ashamed and who correctly handles the word of truth."
                            )
                        ),
                    ]
                ),

                Task(
                    summary="Database Models + Alembic Migrations",
                    labels=["backend","db","alembic"],
                    description="Define Station/Observation/Aggregate models; migrations; time-series indexes; API alignment; query tests.",
                    subtasks=[
                        Subtask(
                            summary="Define ORM models and enums",
                            labels=["backend","db"],
                            description="Station(type/name/lat/lon), Observation(ts/metrics), AggregateHourly/Daily; composite PKs; enums for PWS/NDBC/AIRPORT."
                                "*Faith Integration*\n"
                                "You must have accurate and honest weights and measures, so that you may live long in the land the Lord your God is giving you. "
                        ),
                        Subtask(
                            summary="Alembic migrations & autogenerate",
                            labels=["backend","alembic"],
                            description="Init Alembic; target metadata; initial migration; test upgrade/downgrade in staging."
                                "*Faith Integration*\n"
                                "Give careful thought to the paths for your feet and be steadfast in all your ways."
                        ),
                        Subtask(
                            summary="Index strategy for time-series",
                            labels=["backend","db","performance"],
                            description="Add (station_id, ts) composite index; EXPLAIN ANALYZE typical windows; adjust as needed."
                                "*Faith Integration*\n"
                                "If the ax is dull and its edge unsharpened, more strength is needed, but skill will bring success."
                        ),
                        Subtask(
                            summary="Schema ↔ API contract alignment",
                            labels=["backend","api"],
                            description="DB→API mapping with field names/units; constraints against impossible values."
                                "*Faith Integration*\n"
                                "Honest scales and balances belong to the Lord; all the weights in the bag are of his making."
                        ),
                        Subtask(
                            summary="Query tests (hourly/daily windows)",
                            labels=["tests","db"],
                            description="Micro-benchmarks for common ranges; assert p95 targets; surface regressions in CI."
                                "*Faith Integration*\n"
                                "Do you not know that in a race all the runners run, but only one gets the prize? Run in such a way as to get the prize."
                        ),
                    ]
                ),

                Task(
                    summary="ETL Package (Bronze → Silver → Gold)",
                    labels=["etl","python"],
                    description="`etl/` modules for fetch/clean/aggregate + CLI; idempotence; dedup keys; normalization; incremental runs; audit log.",
                    subtasks=[
                        Subtask(
                            summary="Package layout & entry points",
                            labels=["etl","python"],
                            description="`etl/bronze_fetch.py`, `silver_clean.py`, `gold_aggregate.py`, `cli.py` with commands and params."
                                "*Faith Integration*\n"
                                "“Who dares despise the day of small things, since the seven eyes of the Lord that range throughout the earth will rejoice when they see the chosen capstone in the hand of Zerubbabel?”"
                        ),
                        Subtask(
                            summary="Idempotent fetch & dedup keys",
                            labels=["etl","db"],
                            description="Natural key (station_id+ts+source) + Postgres UPSERT; batch IDs/checksums; resumable fetch."
                                "*Faith Integration*\n"
                                "who despises a vile person but honors those who fear the Lord; who keeps an oath even when it hurts, and does not change their mind;"
                        ),
                        Subtask(
                            summary="Cleaning & normalization (Silver)",
                            labels=["etl","quality"],
                            description="Canonical units, snake_case, clamp invalids, drop NaN-heavy rows; per-source validation; QA stats."
                                "*Faith Integration*\n"
                                "so that you may be able to discern what is best and may be pure and blameless for the day of Christ,"
                        ),
                        Subtask(
                            summary="Aggregations (Gold)",
                            labels=["etl","db"],
                            description="Hourly mean/min/max/gusts + derived metrics; daily from hourly; UPSERT; test DST/leap."
                                "*Faith Integration*\n"
                                "'For it is: Do this, do that, a rule for this, a rule for that; a little here, a little there.'"
                        ),
                        Subtask(
                            summary="ETL logging table & run audit",
                            labels=["etl","ops"],
                            description="`etl_run` table (stage/times/rows/errors/status); expose via `/api/status`."
                                "*Faith Integration*\n"
                                "Nothing in all creation is hidden from God’s sight. Everything is uncovered and laid bare before the eyes of him to whom we must give account."
                        ),
                        Subtask(
                            summary="Incremental / delta runs",
                            labels=["etl","performance"],
                            description="Track `last_obs_ts`; fetch deltas + 15-min overlap; dedup."
                                "*Faith Integration*\n"
                                "Be very careful, then, how you live—not as unwise but as wise, making the most of every opportunity, because the days are evil."
                        ),
                    ]
                ),

                Task(
                    summary="Data Quality + Caching",
                    labels=["quality","caching","backend"],
                    description="Validators, caching (Redis/in-proc), cache purge on ETL completion, `/api/cache_status`.",
                    subtasks=[
                        Subtask(
                            summary="Lightweight validation checks",
                            labels=["quality","etl"],
                            description="Bounds/monotonic/duplicates/station whitelist; log violations; optional quarantine."
                                "*Faith Integration*\n"
                                "Righteousness guards the person of integrity, but wickedness overthrows the sinner."
                        ),
                        Subtask(
                            summary="Response caching (Redis or in-proc)",
                            labels=["backend","caching"],
                            description="Key by (endpoint, station, period, metric); Cache-Control; invalidate on ETL writes."
                                "*Faith Integration*\n"
                                "When they had all had enough to eat, he said to his disciples, 'Gather the pieces that are left over. Let nothing be wasted.'"
                        ),
                        Subtask(
                            summary="Auto-expire on ETL completion",
                            labels=["backend","caching"],
                            description="Emit event or call admin endpoint to purge affected cache keys; safety TTLs."
                                "*Faith Integration*\n"
                                "They are new every morning; great is your faithfulness."
                        ),
                        Subtask(
                            summary="/api/cache_status & metrics",
                            labels=["backend","observability"],
                            description="Expose hit ratio, key count, memory; protect in prod; tune TTLs."
                                "*Faith Integration*\n"
                                "The one who guards a fig tree will eat its fruit, and whoever protects their master will be honored."
                        ),
                    ]
                ),

                Task(
                    summary="Render Deployment (API + Cron)",
                    labels=["deploy","render","ops"],
                    description="Gunicorn Procfile, secrets/envs, health/readiness, ETL cron (~3h), and observability.",
                    subtasks=[
                        Subtask(
                            summary="Procfile & Gunicorn",
                            labels=["deploy","backend"],
                            description="`web: gunicorn wsgi:app --workers 2 --threads 4 --timeout 60`; validate logs."
                                "*Faith Integration*\n"
                                "Each of you should use whatever gift you have received to serve others, as faithful stewards of God’s grace in its various forms. "
                        ),
                        Subtask(
                            summary="Environment variables & secrets",
                            labels=["deploy","security"],
                            description="DB URL, API keys, allowed origins; separate staging/prod; never commit `.env`."
                                "*Faith Integration*\n"
                                "Whoever derides their neighbor has no sense, but the one who has understanding holds their tongue."
                        ),
                        Subtask(
                            summary="Healthcheck & readiness",
                            labels=["ops","backend"],
                            description="`/healthz` and `/readyz` (DB/cache/migrations); configure Render health checks."
                                "*Faith Integration*\n"
                                "Be on guard! Be alert! You do not know when that time will come."
                        ),
                        Subtask(
                            summary="ETL Cron (every ~3h)",
                            labels=["etl","ops"],
                            description="Render Cron: `python -m etl.cli run-all --since=3h`; capture logs; avoid deploy clashes."
                                "*Faith Integration*\n"
                                "Now when Daniel learned that the decree had been published, he went home to his upstairs room where the windows opened toward Jerusalem. Three times a day he got down on his knees and prayed, giving thanks to his God, just as he had done before."
                        ),
                        Subtask(
                            summary="Observability on Render",
                            labels=["observability","ops"],
                            description="Structured logs (request_id/station_id); track p95 latency & error rates."
                                "*Faith Integration*\n"
                                "Test me, Lord, and try me, examine my heart and my mind;"
                        ),
                    ]
                ),
            ],
        ),

        # 🧪 Epic 3
        Epic(
            summary="Reliability & Validation",
            labels=["validation","tests","roadmap"],
            description="Transform unit tests; API contract & performance; golden-station snapshots + CI diff; wind/wave rose QA; /status freshness monitor.",
            tasks=[

                Task(
                    summary="Transform Unit Tests (Calculator Functions)",
                    labels=["tests","etl"],
                    description="Tests for mean/sum/max/OLS slope with seeded fixtures & edge cases (NaN/empty); DST/leap/UTC offsets.",
                    subtasks=[
                        Subtask(
                            summary="Mean/sum/max/OLS slope tests",
                            labels=["tests","etl"],
                            description="`tests/etl/test_calculators.py` with tiny arrays; assert exact outputs & slope tolerance."
                                "*Faith Integration*\n"
                                "For the Lord gives wisdom; from his mouth come knowledge and understanding."
                        ),
                        Subtask(
                            summary="Fixtures & edge cases",
                            labels=["tests","etl"],
                            description="`tests/data/` JSON/CSV (NaNs, negatives, duplicates); helper loader; documented intent."
                                "*Faith Integration*\n"
                                "I know, my God, that you test the heart and are pleased with integrity. All these things I have given willingly and with honest intent. And now I have seen with joy how willingly your people who are here have given to you."
                        ),
                        Subtask(
                            summary="Coverage for DST/leap/UTC offsets",
                            labels=["tests","time"],
                            description="Edge windows crossing DST and Feb 29; ensure UTC normalization in API time outputs."
                                "*Faith Integration*\n"
                                "My times are in your hands; deliver me from the hands of my enemies, from those who pursue me."
                        ),
                    ]
                ),

                Task(
                    summary="API Contract Tests",
                    labels=["tests","api"],
                    description="JSON schema validation for /api/*; enforce granularity/units/station metadata; performance contract (p95).",
                    subtasks=[
                        Subtask(
                            summary="JSON schema validations for /api/*",
                            labels=["tests","api"],
                            description="Schemas for /api/summary_data, /api/graph_data, /api/status; structured errors."
                                "*Faith Integration*\n"
                                "Every word of God is flawless; he is a shield to those who take refuge in him."
                        ),
                        Subtask(
                            summary="Field names & unit presence",
                            labels=["tests","api"],
                            description="Diff expected vs actual keys; require units for numeric metrics; maintain unit map."
                                "*Faith Integration*\n"
                                "“I the Lord do not change. So you, the descendants of Jacob, are not destroyed. "
                        ),
                        Subtask(
                            summary="Performance contract (p95 latency)",
                            labels=["tests","performance"],
                            description="Benchmark representative endpoints; assert p95 < 250ms; print query plans on regressions."
                                "*Faith Integration*\n"
                                "Never be lacking in zeal, but keep your spiritual fervor, serving the Lord."
                        ),
                    ]
                ),

                Task(
                    summary="Golden-Station Snapshots + CI Diff",
                    labels=["tests","ci","snapshots"],
                    description="Pick 2 PWS + 1 NDBC; store 7-day goldens; CI job diffs outputs with tolerances; doc refresh policy.",
                    subtasks=[
                        Subtask(
                            summary="Choose 2 PWS + 1 NDBC stations",
                            labels=["tests","data"],
                            description="Select stable stations; save API outputs (summary/graph) to `tests/data/golden/` with notes."
                                "*Faith Integration*\n"
                                "This will be my third visit to you. “Every matter must be established by the testimony of two or three witnesses.”"
                        ),
                        Subtask(
                            summary="CI job to diff golden outputs",
                            labels=["ci","tests"],
                            description="GitHub Actions invokes API & diffs vs golden (±0.5% tolerance). Fail on drift; allow manual refresh."
                                "*Faith Integration*\n"
                                "This is what he showed me: The Lord was standing by a wall that had been built true to plumb, with a plumb line in his hand. 8And the Lord asked me, 'What do you see, Amos?' 'A plumb line,' I replied. Then the Lord said, “Look, I am setting a plumb line among my people Israel; I will spare them no longer."
                        ),
                        Subtask(
                            summary="Tolerance & drift notes",
                            labels=["docs","tests"],
                            description="README on interpreting diffs, thresholds, and changelog for golden updates."
                                "*Faith Integration*\n"
                                "Get wisdom, get understanding; do not forget my words or turn away from them."
                        ),
                    ]
                ),

                Task(
                    summary="Wind/Wave Roses QA",
                    labels=["tests","charts","qa"],
                    description="Automated QA for bin distributions & wrap-around; visual QA exports for manual review.",
                    subtasks=[
                        Subtask(
                            summary="Percentile checks on bin counts",
                            labels=["qa","charts"],
                            description="Compute per-rose stats; flag anomalous bins and excessive calms; persist QA per run."
                                "*Faith Integration*\n"
                                "let God weigh me in honest scales and he will know that I am blameless—"
                        ),
                        Subtask(
                            summary="Wrap-around integrity (0/360)",
                            labels=["qa","charts"],
                            description="Test near-0°/360° bins; assert sum(bins)==N."
                                "*Faith Integration*\n"
                                "Every good and perfect gift is from above, coming down from the Father of the heavenly lights, who does not change like shifting shadows."
                        ),
                        Subtask(
                            summary="Visual QA exports",
                            labels=["qa","charts","ci"],
                            description="Generate PNG/SVG reports with metadata footer; attach to CI artifacts."
                                "*Faith Integration*\n"
                                "For the revelation awaits an appointed time; it speaks of the end and will not prove false. Though it linger, wait for it; it will certainly come and will not delay."
                        ),
                    ]
                ),

                Task(
                    summary="/status Freshness Monitor",
                    labels=["status","ops","backend","frontend"],
                    description="Track last_etl_run & last_obs_ts; expose /api/status (200/503); alert on staleness; frontend status widget.",
                    subtasks=[
                        Subtask(
                            summary="Track last_etl_run & last_obs_ts",
                            labels=["backend","db"],
                            description="Add `system_status` or columns updated by ETL; per-station last_obs_ts; ensure UTC."
                                "*Faith Integration*\n"
                                "Teach us to number our days, that we may gain a heart of wisdom."
                        ),
                        Subtask(
                            summary="/api/status endpoint",
                            labels=["backend","api","status"],
                            description="Return freshness summary & samples; set HTTP 200/503 by threshold for external monitors."
                                "*Faith Integration*\n"
                                "'In the same way, let your light shine before others, that they may see your good deeds and glorify your Father in heaven.'"
                        ),
                        Subtask(
                            summary="Alerting on staleness",
                            labels=["ops","status"],
                            description="Email/webhook on threshold breach; rate-limit; log alerts with remediation hints."
                                "*Faith Integration*\n"
                                "But we prayed to our God and posted a guard day and night to meet this threat."
                        ),
                        Subtask(
                            summary="Frontend status widget",
                            labels=["frontend","ui","status"],
                            description="Banner/card ‘Data fresh as of …’ with color states; link to details; short client cache. Faith Integration Transparency invites trust and patience"
                                "*Faith Integration*\n"
                                "Let us not become weary in doing good, for at the proper time we will reap a harvest if we do not give up. "
                        ),
                    ]
                ),
            ],
        ),
    ]

# ---------- Creator ----------
def create_backlog(
    backlog: List[Epic],
    project_key: str,
    link_tasks_to_epics: bool = True,
    dry_run: bool = False
):
    is_company, epic_link_field = project_uses_company_managed_epic_link()
    print(f"ℹ️ Epic linking mode: {'company-managed' if is_company else 'team-managed'}"
          f"{' via ' + epic_link_field if epic_link_field else ''}")

    created = {"epics": {}, "tasks": {}, "subtasks": {}}

    for epic in backlog:
        # 1) Create Epic (idempotent by summary)
        existing = search_issue_by_summary(project_key, epic.summary)
        if existing:
            epic_key = existing
            print(f"↩️  Epic exists: {epic_key}  {epic.summary}")
        else:
            epic_fields = {
                "project": {"key": project_key},
                "summary": epic.summary,
                "description": epic.description,
                "issuetype": {"name": "Epic"},
                "labels": epic.labels or []
            }
            if epic.priority:
                epic_fields["priority"] = {"name": epic.priority}

            if dry_run:
                print(f"[DRY-RUN] Would create Epic: {epic.summary}")
                epic_key = f"{project_key}-EPIC-TBD"
            else:
                epic_issue = create_issue_with_retry(epic_fields)
                epic_key = epic_issue.key
                print(f"✅ Created Epic: {epic_key}  {epic.summary}")
        created["epics"][epic.summary] = epic_key

        # 2) Create Tasks
        for task in epic.tasks:
            existing_task = search_issue_by_summary(project_key, task.summary)
            if existing_task:
                task_key = existing_task
                print(f"↩️  Task exists: {task_key}  {task.summary}")
            else:
                task_fields = {
                    "project": {"key": project_key},
                    "summary": task.summary,
                    "description": task.description,
                    "issuetype": {"name": "Task"},
                    "labels": task.labels or []
                }
                if task.priority:
                    task_fields["priority"] = {"name": task.priority}

                # Link Task → Epic
                if link_tasks_to_epics and not dry_run:
                    if is_company and epic_link_field:
                        # Company-managed: set 'Epic Link' custom field to epic key
                        task_fields[epic_link_field] = created["epics"][epic.summary]
                    else:
                        # Team-managed often supports 'parent' for epic parenting
                        # Many team-managed projects accept 'parent' for Task->Epic
                        task_fields["parent"] = {"key": created["epics"][epic.summary]}

                if dry_run:
                    print(f"[DRY-RUN] Would create Task under Epic {epic_key}: {task.summary}")
                    task_key = f"{project_key}-TASK-TBD"
                else:
                    task_issue = create_issue_with_retry(task_fields)
                    task_key = task_issue.key
                    print(f"  ✅ Created Task: {task_key}  {task.summary}")
            created["tasks"][task.summary] = task_key

            # 3) Create Subtasks
            for sub in task.subtasks:
                existing_sub = search_issue_by_summary(project_key, sub.summary)
                if existing_sub:
                    sub_key = existing_sub
                    print(f"  ↩️  Sub-task exists: {sub_key}  {sub.summary}")
                else:
                    sub_fields = {
                        "project": {"key": project_key},
                        "summary": sub.summary,
                        "description": sub.description,
                        "issuetype": {"name": "Sub-task"},
                        "labels": sub.labels or [],
                        "parent": {"key": task_key},
                    }
                    if sub.priority:
                        sub_fields["priority"] = {"name": sub.priority}

                    if dry_run:
                        print(f"[DRY-RUN] Would create Sub-task under {task_key}: {sub.summary}")
                        sub_key = f"{project_key}-SUBT-TBD"
                    else:
                        sub_issue = create_issue_with_retry(sub_fields)
                        sub_key = sub_issue.key
                        print(f"    ✅ Created Sub-task: {sub_key}  {sub.summary}")
                created["subtasks"][sub.summary] = sub_key

    return created

# ---------- Main ----------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Create Jira Epics → Tasks → Sub-tasks for a project")
    ap.add_argument("--project", default=PROJ, help="Project key (default from JIRA_PROJECT_KEYS)")
    ap.add_argument("--no-epic-link", action="store_true", help="Do not link tasks to epics")
    ap.add_argument("--dry-run", action="store_true", help="Print actions without creating issues")
    args = ap.parse_args()

    backlog = get_backlog()
    out = create_backlog(
        backlog,
        project_key=args.project,
        link_tasks_to_epics=not args.no_epic_link,
        dry_run=args.dry_run
    )
    print("\n🎉 Done.")
