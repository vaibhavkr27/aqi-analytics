"""
CityAir — Indian Air Quality Analytics Dashboard.
"""

from __future__ import annotations

import sqlite3
import sys
import subprocess
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from data.geocoder import geocode_city


DB_PATH = PROJECT_ROOT / "db" / "aqi.db"

def city_exists(city_name: str) -> bool:
    """Check whether the city already exists in SQLite."""

    if not DB_PATH.exists():
        return False

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM cities
            WHERE LOWER(city_name) = LOWER(?)
            LIMIT 1
            """,
            (city_name,),
        ).fetchone()

    return row is not None


def ingest_searched_city(city_name: str) -> tuple[bool, str]:
    """
    Run the existing ingestion pipeline for a newly searched city.
    """

    ingest_script = PROJECT_ROOT / "data" / "ingest.py"

    if not ingest_script.exists():
        return False, "data/ingest.py was not found."

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(ingest_script),
                city_name,
            ],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )

    except subprocess.TimeoutExpired:
        return False, "Data ingestion timed out after 3 minutes."

    except Exception as exc:
        return False, f"Could not start ingestion: {exc}"

    if result.returncode != 0:
        error_output = result.stderr.strip() or result.stdout.strip()
        return False, error_output

    return True, result.stdout


# ============================================================
# Page
# ============================================================

st.set_page_config(
    page_title="CityAir",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Database helpers
# ============================================================

@st.cache_data(ttl=300)
def load_cities() -> pd.DataFrame:

    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:

        return pd.read_sql_query(
            """
            SELECT
                city_id,
                city_name,
                state,
                latitude,
                longitude
            FROM cities
            ORDER BY city_name
            """,
            conn,
        )


@st.cache_data(ttl=300)
def load_summary() -> pd.DataFrame:

    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:

        return pd.read_sql_query(
            """
            SELECT
                c.city_name,
                c.state,
                r.parameter,
                r.value,
                r.unit,
                r.measured_at
            FROM readings r
            JOIN cities c
                ON c.city_id = r.city_id
            """,
            conn,
            parse_dates=["measured_at"],
        )


def load_city_data(
    city_name: str,
    parameter: str,
) -> pd.DataFrame:

    with sqlite3.connect(DB_PATH) as conn:

        return pd.read_sql_query(
            """
            SELECT
                c.city_name,
                c.state,
                r.parameter,
                r.value,
                r.unit,
                r.measured_at
            FROM readings r
            JOIN cities c
                ON c.city_id = r.city_id
            WHERE c.city_name = ?
              AND r.parameter = ?
            ORDER BY r.measured_at
            """,
            conn,
            params=(city_name, parameter),
            parse_dates=["measured_at"],
        )


def database_stats() -> dict:

    with sqlite3.connect(DB_PATH) as conn:

        cities = conn.execute(
            "SELECT COUNT(*) FROM cities"
        ).fetchone()[0]

        locations = conn.execute(
            "SELECT COUNT(*) FROM locations"
        ).fetchone()[0]

        sensors = conn.execute(
            "SELECT COUNT(*) FROM sensors"
        ).fetchone()[0]

        readings = conn.execute(
            "SELECT COUNT(*) FROM readings"
        ).fetchone()[0]

        latest = conn.execute(
            "SELECT MAX(measured_at) FROM readings"
        ).fetchone()[0]

    return {
        "cities": cities,
        "locations": locations,
        "sensors": sensors,
        "readings": readings,
        "latest": latest,
    }


# ============================================================
# Header
# ============================================================

st.title("🌫️ CityAir")

st.markdown(
    """
    ### Indian Air Quality Intelligence

    Explore real air-quality measurements from OpenAQ monitoring
    stations across Indian cities.
    """
)


# ============================================================
# Search
# ============================================================

st.subheader("Search a city")

search_col, button_col = st.columns(
    [5, 1]
)

with search_col:

    search_query = st.text_input(
        "City",
        placeholder="e.g. Jaipur, Jamshedpur, Delhi",
        label_visibility="collapsed",
    )

with button_col:

    search_clicked = st.button(
        "Search",
        type="primary",
        use_container_width=True,
    )


if search_clicked:

    if not search_query.strip():

        st.warning(
            "Enter an Indian city name."
        )

    else:

        with st.spinner(
            f"Finding {search_query.strip()}..."
        ):

            try:

                result = geocode_city(
                    search_query
                )

            except Exception as exc:

                st.error(
                    f"Geocoding failed: {exc}"
                )

                result = None

        if not result:

            st.error(
                "We couldn't find that city in India."
            )

        else:

            st.session_state["search_result"] = result


# ============================================================
# Search result
# ============================================================

search_result = st.session_state.get(
    "search_result"
)


if search_result:

    st.success(
        f"Found: {search_result['display_name']}"
    )

    st.caption(
        f"Coordinates: "
        f"{search_result['latitude']:.4f}, "
        f"{search_result['longitude']:.4f}"
    )

    searched_city = search_query.strip()

    if city_exists(searched_city):

        st.success(
            f"{searched_city} is already available in CityAir."
        )

        st.session_state["selected_city"] = searched_city

    else:

        with st.spinner(
            f"Fetching OpenAQ monitoring data for {searched_city}..."
        ):

            success, output = ingest_searched_city(
                searched_city
            )

        if success:

            st.success(
                f"✓ {searched_city} has been added to CityAir."
            )

            st.session_state["selected_city"] = searched_city

            # Clear cached database data so the new city appears.
            load_cities.clear()
            load_summary.clear()
            load_city_data.clear()

            st.rerun()

        else:

            st.error(
                f"Could not load OpenAQ data for {searched_city}."
            )

            with st.expander("Ingestion details"):

                st.code(
                    output,
                    language="text",
                )


# ============================================================
# Database status
# ============================================================

if not DB_PATH.exists():

    st.error(
        "Database not found. Run the ingestion pipeline first."
    )

    st.stop()


stats = database_stats()


# ============================================================
# KPI
# ============================================================

cols = st.columns(5)

cols[0].metric(
    "Cities",
    f"{stats['cities']:,}",
)

cols[1].metric(
    "Locations",
    f"{stats['locations']:,}",
)

cols[2].metric(
    "Sensors",
    f"{stats['sensors']:,}",
)

cols[3].metric(
    "Readings",
    f"{stats['readings']:,}",
)

latest = stats["latest"]

if latest:

    latest_dt = pd.to_datetime(
        latest,
        utc=True,
    )

    cols[4].metric(
        "Latest reading",
        latest_dt.strftime(
            "%d %b %H:%M UTC"
        ),
    )


# ============================================================
# Sidebar
# ============================================================

cities_df = load_cities()
all_data = load_summary()

if all_data.empty:

    st.warning(
        "The database contains no readings yet."
    )

    st.stop()


st.sidebar.header(
    "Dashboard filters"
)

available_cities = sorted(
    all_data["city_name"].unique()
)

preferred_city = st.session_state.get("selected_city")

if preferred_city in available_cities:
    default_index = available_cities.index(preferred_city)
else:
    default_index = 0

selected_city = st.sidebar.selectbox(
    "City",
    available_cities,
    index=default_index,
)

available_parameters = sorted(
    all_data[
        all_data["city_name"] == selected_city
    ]["parameter"].dropna().unique()
)

selected_parameter = st.sidebar.selectbox(
    "Pollutant",
    available_parameters,
)


# ============================================================
# City data
# ============================================================

city_data = load_city_data(
    selected_city,
    selected_parameter,
)

if city_data.empty:

    st.warning(
        "No readings are available for this selection."
    )

    st.stop()


city_data["measured_at"] = pd.to_datetime(
    city_data["measured_at"],
    utc=True,
)


latest_reading = city_data.iloc[-1]

latest_value = latest_reading["value"]

unit = latest_reading["unit"]


# ============================================================
# Current snapshot
# ============================================================

st.divider()

st.subheader(
    f"{selected_city} — Current snapshot"
)

k1, k2, k3, k4 = st.columns(4)


k1.metric(
    f"Latest {selected_parameter.upper()}",
    f"{latest_value:.1f} {unit}",
)


last_24h = city_data[
    city_data["measured_at"]
    >= city_data["measured_at"].max()
    - pd.Timedelta(hours=24)
]


if not last_24h.empty:

    k2.metric(
        "24h average",
        f"{last_24h['value'].mean():.1f} {unit}",
    )


last_7d = city_data[
    city_data["measured_at"]
    >= city_data["measured_at"].max()
    - pd.Timedelta(days=7)
]


if not last_7d.empty:

    k3.metric(
        "7d average",
        f"{last_7d['value'].mean():.1f} {unit}",
    )


if len(last_7d) > 1:

    change = (
        (
            last_7d["value"].iloc[-1]
            /
            last_7d["value"].iloc[0]
        )
        - 1
    ) * 100

    k4.metric(
        "7d change",
        f"{change:+.1f}%",
    )


# ============================================================
# Trend
# ============================================================

st.subheader(
    f"{selected_parameter.upper()} — Historical trend"
)

trend = (
    city_data
    .assign(
        date=city_data["measured_at"].dt.date
    )
    .groupby("date", as_index=False)["value"]
    .mean()
)

fig = px.line(
    trend,
    x="date",
    y="value",
    markers=True,
    labels={
        "date": "Date",
        "value": f"{selected_parameter.upper()} ({unit})",
    },
)

fig.update_layout(
    hovermode="x unified",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# City ranking
# ============================================================

st.subheader(
    f"Current {selected_parameter.upper()} ranking"
)

latest_by_city = (
    all_data[
        all_data["parameter"]
        == selected_parameter
    ]
    .sort_values("measured_at")
    .groupby("city_name")
    .tail(1)
    .sort_values("value", ascending=False)
)


fig_rank = px.bar(
    latest_by_city,
    x="value",
    y="city_name",
    orientation="h",
    labels={
        "value": f"{selected_parameter.upper()} ({unit})",
        "city_name": "City",
    },
)

st.plotly_chart(
    fig_rank,
    use_container_width=True,
)


# ============================================================
# Insight
# ============================================================

st.subheader("📌 Key insight")

if len(last_7d) >= 2:

    avg_7d = last_7d["value"].mean()

    city_values = (
        latest_by_city["value"]
    )

    national_average = (
        city_values.mean()
        if not city_values.empty
        else avg_7d
    )

    difference = (
        (avg_7d / national_average) - 1
    ) * 100 if national_average else 0

    direction = (
        "above"
        if difference >= 0
        else "below"
    )

    st.info(
        f"{selected_city}'s 7-day average "
        f"{selected_parameter.upper()} concentration "
        f"is {abs(difference):.1f}% {direction} "
        f"the current tracked-city average. "
        f"The latest reading is "
        f"{latest_value:.1f} {unit}."
    )

else:

    st.info(
        "More observations are needed to generate "
        "a meaningful trend insight."
    )


# ============================================================
# Data quality
# ============================================================

with st.expander("Data quality & methodology"):

    st.markdown(
        f"""
        **Data source:** OpenAQ

        **Geocoding:** OpenStreetMap Nominatim

        **Current city:** {selected_city}

        **Pollutant:** {selected_parameter.upper()}

        **Observations available:** {len(city_data):,}

        **Latest observation:** {latest_reading['measured_at']}

        Measurements are validated to remove missing and
        negative pollutant values. Duplicate sensor/timestamp
        observations are prevented at the database level.
        """
    )