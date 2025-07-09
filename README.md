# 🌤 Weather Dashboard — Faith-Inspired Full-Stack Data Project

> “Whatever you do, work at it with all your heart, as working for the Lord…” — Colossians 3:23

## 🙏 Purpose

This project was born from a desire to honor God through the technical skills He’s given me. It’s a full-stack weather monitoring dashboard that captures, stores, and visualizes real-time and historical weather data using personal weather stations (PWS) and The Weather Company API.

---

## 🌍 Overview

The Weather Dashboard combines automated data ingestion, robust backend processing, and an interactive React UI to provide real-time and historical weather insight across multiple PWS sensors.

### Key Capabilities:
- Fetches hourly & live PWS data via The Weather Company API
- Parses raw JSON → cleans → PostgreSQL database
- Visualizes summaries, graphs, and real-time conditions
- Includes fallback logic when live API data is unavailable
- Supports multiple stations and time filters
- Deployed with automation on Render and Vercel

---

## 🧰 Tech Stack

| Layer      | Technology                           |
|------------|---------------------------------------|
| Frontend   | React, Chart.js, Axios                |
| Backend    | Flask (Python), Pandas, SQLAlchemy    |
| Database   | PostgreSQL (Render-hosted)            |
| API Source | The Weather Company (IBM PWS)         |
| Deployment | Vercel (frontend), Render (backend)   |
| Automation | Render Cron Jobs (every 2–4 hrs)      |

---

## 🏗️ Project Architecture

weather_dashboard/
├── backend/
│ ├── fetch/ # Scripts to pull & transform raw weather data
│ ├── aggregate_to_hourly.py # Hourly aggregation script
│ ├── aggregate_to_daily.py # Daily aggregation script
│ ├── process_weather_data.py# Cleans raw → structured tables
│ ├── app.py # Flask API endpoints
│ └── config/ # Field maps, helpers, logging config
├── data/ # Raw JSON data (persisted only in dev)
├── frontend/weather-ui/ # React weather dashboard UI
├── run_pipeline.py # Orchestrates full ETL pipeline
├── .env # API keys & DB URL (excluded from repo)
└── README.md

yaml
Copy
Edit

---

## ✨ Skills in Action

This project showcases:

- 🧱 Full-stack architecture (React + Flask)
- 🛠 ETL & data engineering (JSON → PostgreSQL)
- 📈 Interactive frontend with graphs, filters, summary cards
- 🔄 Real-time + historical sync logic with API fallback
- 🖥 DevOps readiness (Vercel + Render deploys, env management, cron automation)

---

## 🚀 Feature Highlights

- ✅ **Historical Weather Sync** — ingest past-year JSON via PWS API
- ✅ **Live Conditions Endpoint** — `/api/current_data_live` with fallback
- ✅ **Summary Stats API** — `/api/summary_data?station_id=X&period=7d`
- ✅ **Graph API** — `/api/graph_data?station_id=X&period=30d&column=temp_avg`
- ✅ **New `/status` Route** — station health check: record count & last update
- ✅ **PostgreSQL Support** — scalable, cloud-hosted DB with indexing
- ✅ **Cron-Scheduled Pipeline** — fetch, process & store every 2–4 hours
- ✅ **Secure .env Management** — API keys not exposed

---

## 🛣 Roadmap

### ✅ Completed
- PostgreSQL database setup + migrations from SQLite
- Render deployment of backend with logging
- Automated ETL via `run_pipeline.py` in Render Cron
- Live & historical sync, fallback logic
- Mobile-aware UI, React dashboard, and weather graphs

### 🚧 In Progress
- UI weather cards styling & responsiveness polish
- Webhook alerts or email on ETL failure
- Optional advanced filtering or QA rules on raw data
- More robust sensor validation (NaN, repeats, out-of-range)

---

## 🛡 Data Quality Filtering (Planned)

To improve reliability, upcoming logic may:

- Exclude readings where:
  - temp/humidity/wind are `NaN`, negative, or zero (if invalid)
  - sensor values are unchanged for extended periods
- Flag abnormal spikes or gaps

Estimated impact: could remove 3–10% of low-quality rows per station (varies by sensor).

---

## 🙌 Final Word

This dashboard reflects not just technical skill, but a desire to create tools that serve others, honor God, and foster learning. Every script, endpoint, and design decision is rooted in purpose.

> “To Him be the glory… throughout all generations, forever and ever. Amen.” — Ephesians 3:21

---

## 📫 Want to Connect?

Open to questions, collaboration, or encouragement — especially among developers of faith, data enthusiasts, and those working in weather, civic tech, or educational tools.
