# CityAir — Air Quality Analytics & Live Dashboard

End-to-end air quality analytics project: real public API data → SQLite →
SQL analysis → live Streamlit dashboard, deployed for free.

## What this project demonstrates
- Pulling and refreshing real-world data from a public API (not a static Kaggle CSV)
- Data cleaning / validation with pandas
- Relational schema design + SQL analysis (trends, rankings, correlations)
- Turning analysis into a business/policy-style recommendation
- Deploying a live, interactive dashboard a recruiter can open with one click

## Project structure
```
aqi-analytics/
├── data/
│   └── ingest.py          # pulls AQI data from OpenAQ API, cleans it, loads to SQLite
├── db/
│   ├── schema.sql         # table definitions
│   └── aqi.db              # created automatically (SQLite file)
├── analysis/
│   └── queries.sql         # the SQL questions this project answers
├── app/
│   └── app.py               # Streamlit dashboard
├── .streamlit/
│   └── config.toml          # theme config
├── requirements.txt
└── README.md
```

## Setup (local)

1. Create a free OpenAQ API key: https://explore.openaq.org/register
   (needed because OpenAQ v3 requires a key — it's free, instant)

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set your API key as an environment variable:
```bash
export OPENAQ_API_KEY="your_key_here"     # Windows: set OPENAQ_API_KEY=your_key_here
```

4. Build the database:
```bash
python data/ingest.py
```
This fetches recent AQI readings for a set of Indian cities, cleans them, and
writes them into `db/aqi.db`.

5. Run the dashboard locally:
```bash
streamlit run app/app.py
```

## Deploying it live (free)

1. Push this folder to a public GitHub repo.
2. Go to https://share.streamlit.io → "New app" → connect your GitHub repo →
   set main file path to `app/app.py`.
3. In the app's "Secrets" settings, add:
```
OPENAQ_API_KEY = "your_key_here"
```
4. Deploy. You'll get a public URL like `https://yourname-cityair.streamlit.app`
   — put this link on your resume and LinkedIn.

## Suggested resume bullet (fill in real numbers once you have them)
> Built and deployed CityAir, a live air-quality analytics dashboard covering
> N Indian cities; automated ingestion pipeline pulls and refreshes data from
> a public API, SQL-based analysis identifies seasonal pollution spikes and
> city rankings, deployed on Streamlit Cloud — [live link].

## The one thing that makes this worth showing
Don't just show charts. In the dashboard's "Insight" section, write out 2-3
sentences like:
> "AQI in Delhi rises ~45% between October and December compared to the
> yearly average, consistent with stubble-burning season — worst affected:
> [area]. Recommendation: [x]."
That sentence is what an interviewer remembers, not the chart.

## Extending it later (only if the core is rock-solid first)
- Fold in your own ESP32/IoT sensor readings as a second data source and
  compare against the public API data for your city
- Add a simple 7-day forecast (moving average, not ML, to start)
- Add a "compare two cities" view
