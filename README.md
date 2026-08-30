<div align="center">

# 🌫️ AeroIQ
### An End-to-End Air Quality Analytics Project

**From raw sensor data to statistical insight: a real-world data analysis pipeline covering data acquisition, cleaning, EDA, anomaly detection, and insight generation — served through an interactive dashboard.**

![Python](https://img.shields.io/badge/Python-Data%20Analysis-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-EDA%20%26%20Analytics-150458?logo=pandas&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-SQLite-003B57?logo=sqlite&logoColor=white)
![Statistics](https://img.shields.io/badge/Statistics-Anomaly%20Detection-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-Serving%20Layer-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Dashboard-61DAFB?logo=react&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

<br>



## 📌 The Question This Project Answers

*Given raw, messy, real-world air-quality sensor data for any Indian city — can I turn it into a trustworthy AQI score, spot the patterns and anomalies that matter, and explain them in plain language?*

AeroIQ is my answer: a full analytics pipeline, not just a dashboard. Type a city, and it geocodes it, pulls live monitoring-station data, cleans and processes it, applies the official CPCB AQI methodology, runs statistical analysis on top, and generates written insights — for **any** city, not a fixed pre-loaded list.

## 🔍 The Analysis Workflow

```
Raw API data  →  Data Cleaning  →  Feature Engineering  →  EDA
→  AQI Calculation (CPCB methodology)  →  Statistical Analysis
→  Anomaly Detection  →  Insight Generation  →  Dashboard
```

**Proof it works on unseen data:** run it on **Jaipur** — a city with zero pre-loaded records — and the pipeline still geocodes it, finds the nearest real monitoring station (1.94 km away), pulls 3,547 readings, and produces a full report on the fly.

## 🧮 Core Analytical Work

This is where most of the actual effort went:

- **Data cleaning & preprocessing** — timestamp normalization (UTC → IST), unit standardization, missing-value and duplicate handling across 6 pollutants (PM2.5, PM10, NO₂, SO₂, O₃, CO)
- **Feature engineering** — derived fields (`hour`, `day_of_week`, `is_statistical_anomaly`, `robust_z_score`) built for downstream analysis
- **Exploratory data analysis** — descriptive statistics per pollutant (mean, median, std dev, P95/P99), daily and hourly trend analysis, weekday-vs-weekend comparisons, and a pollutant correlation matrix
- **AQI calculation** — CPCB-methodology sub-index computation via breakpoint interpolation, with minimum-observation thresholds before a score is produced
- **Anomaly detection** — robust z-score-based outlier detection against local baselines to surface real pollution spikes, not noise
- **Insight generation** — analytical output translated into plain-language findings, e.g. *"PM2.5 spiked 1612% above its local baseline at 5 PM"* — the kind of storytelling that turns numbers into a decision-ready narrative
- **SQL-backed data layer** — SQLite used as a queryable local warehouse (cities, stations, sensors, readings), with case-insensitive lookups and de-duplicated inserts



## 🛠️ Tools & Techniques

| Category | Tools |
|---|---|
| Data wrangling & EDA | **Pandas**, Python |
| Data storage & querying | **SQL** (SQLite) |
| Statistical methods | Breakpoint interpolation, robust z-score anomaly detection, correlation analysis |
| Data sourcing | OpenAQ API, OpenStreetMap Nominatim (geocoding) |
| Serving & visualization | FastAPI, React, Recharts |

## 🚀 Quick Start

```bash
# analysis / API layer
pip install -r requirements.txt
cp .env.example .env      # add OPENAQ_API_KEY
uvicorn api.main:app --reload

# dashboard
cd frontend && npm install && npm run dev
```

```bash
curl "http://127.0.0.1:8000/api/report?city=Jaipur"
```

## ⚠️ Honest Notes on Methodology

AQI follows CPCB *methodology*, not an official CPCB live feed · city coverage depends on nearby OpenAQ station availability · reports reflect the latest cached observations, not real-time conditions · no external weather/traffic variables or ML models are used — the analysis is fully statistical and transparent.

## 🔭 Next Steps

Extend correlation analysis with weather variables · add Power BI/Tableau export for stakeholder reporting · scheduled data refresh · broader city coverage.

---

<div align="center">

MIT Licensed · Data analytics portfolio project

</div>