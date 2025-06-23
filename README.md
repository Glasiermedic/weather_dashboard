# 🌤 Weather Dashboard — Faith-Inspired Full-Stack Data Project

> “Whatever you do, work at it with all your heart, as working for the Lord…” — Colossians 3:23

## 🙏 Purpose

This project was born from a desire to honor God through the technical skills He’s given me. It’s a full-stack weather monitoring dashboard that captures, stores, and visualizes real-time and historical weather data using personal weather stations (PWS) and The Weather Company API.

---

## 🌍 Overview

The Weather Dashboard combines automated data ingestion, robust backend processing, and an interactive React UI to provide clean, real-time insight into weather conditions across multiple sensors.

### Key Capabilities:
- Fetches hourly & live PWS data via Weather Company API
- Processes raw JSON → CSV → SQLite
- Displays summary stats, historical charts, and real-time conditions
- Supports filtering by station, time range, and metric
- Includes fallback logic when live API data is unavailable
- Modular setup for deployment and automation

---

## 🧰 Tech Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Frontend   | React, Chart.js, Axios               |
| Backend    | Flask (Python), Pandas, SQLite       |
| Data API   | The Weather Company (IBM PWS)        |
| Deployment | Vercel (frontend), Render (planned)  |
| Automation | Task Scheduler, batch scripts, cron  |

---

## 🏗️ Project Architecture

weather_dashboard/
├── backend/

│ ├── fetch/ # Weather data fetch scripts

│ ├── process_weather_data.py # Cleans and loads to SQLite

│ ├── app.py # Flask backend API

│ └── data_exports/ # SQLite DB and export CSVs

├── data/ # Raw JSON storage by station

├── frontend/

│ └── weather-ui/ # React UI components

├── run_pipeline.py # End-to-end pipeline runner

├── .env # API key (not committed)

└── README.md


---

## ✨ Skills in Action

While the project reflects a range of modern data and web development skills:

- Software architecture (modular Flask + React)
- Data engineering (ETL pipelines, JSON → DB)
- UI design (dynamic charts, dropdowns, mobile layout)
- Automation (pipelines, scheduled syncs, fallback logic)
- DevOps readiness (deployment configs, `.env`, logging)

> “Every good and perfect gift is from above…” — James 1:17

---

## 🚀 Feature Highlights

- ✅ **Historical Weather Sync** — fetches & stores 2025+ data
- ✅ **Real-Time API Peek** — `/api/current_data_live` with SQLite fallback
- ✅ **Graphing Engine** — chart.js + custom selectors for station/metric/time
- ✅ **Weather Summary UI** — averages, highs/lows, trends
- ✅ **Interactive Frontend** — built in React, state-aware
- ✅ **SQLite Aggregation** — hourly & daily metrics with clean schema
- ✅ **File Path & Env Fixes** — stable across dev folders
- ⏳ **Mobile Design Polish** — in progress
- ⏳ **Deployment to Vercel + Render** — planned

---

## 🛣 Roadmap

### ✅ Completed
- Historical and current data ingestion
- SQLite-backed graphing and summaries
- Live API integration with graceful fallback
- Modular, testable Flask + React integration

### 🚧 In Progress
- Responsive weather cards & visual polish
- Vercel frontend deployment
- Backend deployment via Render or Vercel functions
- Logging system (rotating file + structured events)
- Optional webhook alerts after updates

---

## 🙌 Final Word

This dashboard is more than just a technical project — it’s a reflection of what I believe, it is a tool to connect and serve others: God equips us not only to build but to serve. 

> “To Him be the glory… throughout all generations, forever and ever. Amen.” — Ephesians 3:21

---

## 📫 Want to Connect?

Feel free to fork, explore, or reach out. Feedback is welcome — especially from fellow developers of faith or others building weather, data, or automation tools.
