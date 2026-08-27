

# CityAir 🌫️

Real-time air quality analytics for Indian cities using public air-quality data.

CityAir lets users search for a city, find the nearest available OpenAQ monitoring station, retrieve air-quality measurements, and explore the data through an interactive dashboard.

## Features

- 🔎 Search for Indian cities
- 📍 Find nearby OpenAQ monitoring stations
- 🌫️ Track PM2.5, PM10, NO₂, O₃, SO₂ and CO
- 📊 Interactive air-quality charts
- 📈 Historical pollutant trends
- 🗄️ SQLite database for storing measurements
- 🔄 Automated data refresh with GitHub Actions
- 🚀 Streamlit dashboard

## How It Works

City Search  
↓  
Geocoding  
↓  
Latitude / Longitude  
↓  
Nearby OpenAQ Stations  
↓  
Nearest Available Station  
↓  
Air Quality Measurements  
↓  
SQLite Database  
↓  
Streamlit Dashboard

## Tech Stack

* Python
* OpenAQ API
* Geocoding API
* Pandas
* SQLite
* SQL
* Plotly
* Streamlit
* GitHub Actions

## Project Structure

```text
aqi-analytics/
│
├── app/
│   └── app.py              # Streamlit dashboard
│
├── data/
│   ├── ingest.py           # Data ingestion pipeline
│   └── geocoder.py         # City geocoding
│
├── db/
│   ├── schema.sql          # Database schema
│   └── aqi.db              # SQLite database
│
├── analysis/
│   └── queries.sql         # SQL analysis queries
│
├── .github/
│   └── workflows/
│       └── refresh-data.yml
│
├── .streamlit/
│   └── config.toml
│
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/aqi-analytics.git
cd aqi-analytics
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure OpenAQ API Key

Windows PowerShell:

```powershell
$env:OPENAQ_API_KEY="your_api_key"
```

macOS / Linux:

```bash
export OPENAQ_API_KEY="your_api_key"
```

### 5. Run the dashboard

```bash
streamlit run app/app.py
```

## Data Ingestion

The ingestion pipeline can fetch air-quality data for a city:

```bash
python data/ingest.py Delhi
```

Example:

```bash
python data/ingest.py Mumbai
```

The pipeline:

1. Resolves the city using geocoding
2. Finds nearby OpenAQ monitoring stations
3. Selects a suitable station
4. Retrieves available sensors and measurements
5. Validates the data
6. Stores the results in SQLite

## Database

CityAir uses SQLite with the following structure:

```text
City
  │
  └── Monitoring Location
          │
          └── Sensor
                │
                └── Reading
```

This allows the project to keep city, monitoring-station, sensor, and measurement data organized and enables SQL-based analysis.

## Data Source

Air-quality measurements are provided by the OpenAQ API.

City locations are resolved using a geocoding service before searching for nearby monitoring stations.

## Automated Data Refresh

GitHub Actions is used to periodically refresh the stored air-quality data.

The OpenAQ API key is stored securely as a GitHub Actions secret:

```text
OPENAQ_API_KEY
```

API keys are never stored directly in the repository.

## Deployment

The dashboard can be deployed using Streamlit Community Cloud.

```text
GitHub
   ↓
Streamlit Community Cloud
   ↓
CityAir Dashboard
```

## Project Goal

CityAir demonstrates a complete real-world data workflow:

```text
External APIs
     ↓
Data Ingestion
     ↓
Data Validation
     ↓
Database
     ↓
SQL Analytics
     ↓
Visualization
     ↓
Web Dashboard
     ↓
Automated Updates
```

The project uses live public data rather than relying on a static dataset.

## License

This project is built for educational and portfolio purposes.

