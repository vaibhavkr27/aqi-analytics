from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import sys

import pandas as pd


# ============================================================
# Project configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

DB_PATH = PROJECT_DIR / "db" / "aqi.db"

# ============================================================
# Internal database loader
# ============================================================

def _load_city_data(
    conn: sqlite3.Connection,
    city_name: str,
) -> pd.DataFrame:
    """
    Load already-stored readings for a city.
    """

    query = """
        SELECT
            r.measured_at,
            r.parameter,
            r.value,
            r.unit
        FROM readings r
        JOIN cities c
            ON c.city_id = r.city_id
        WHERE LOWER(c.city_name) = LOWER(?)
        ORDER BY r.measured_at
    """

    return pd.read_sql_query(
        query,
        conn,
        params=(city_name,),
    )


# ============================================================
# Dynamic ingestion
# ============================================================

def _ingest_city(
    city_name: str,
) -> None:
    """
    Fetch air-quality data for a city that is not
    currently available in the local database.

    The existing ingestion pipeline handles:
    - geocoding
    - nearby OpenAQ station discovery
    - sensor selection
    - hourly data retrieval
    - SQLite storage
    """

    # Imported here to avoid unnecessary imports when
    # existing database data is already available.
    from data.ingest import (
        initialize_database,
        ingest_city,
    )

    from data.geocoder import geocode_city

    city = geocode_city(
        city_name
    )

    if not city:
        raise ValueError(
            f"Could not find '{city_name}'."
        )

    now = datetime.now(
        timezone.utc
    )

    start = (
        now
        - timedelta(days=30)
    ).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    end = now.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        initialize_database(
            conn
        )

        result = ingest_city(
            conn,
            city["city"],
            city,
            start,
            end,
        )

        if result["status"] != "success":

            raise RuntimeError(
                f"Unable to retrieve AQI data "
                f"for {city_name}: "
                f"{result['status']}"
            )

    finally:

        conn.close()


# ============================================================
# Public city loader
# ============================================================

def get_city_data(
    city_name: str,
) -> pd.DataFrame:
    """
    Return AQI readings for the city requested by
    the user.

    Existing data is reused.

    When the city is not already stored, the existing
    OpenAQ ingestion pipeline is triggered automatically.
    """

    city_name = city_name.strip()

    if not city_name:
        return pd.DataFrame(
            columns=[
                "measured_at",
                "parameter",
                "value",
                "unit",
            ]
        )

    # --------------------------------------------------------
    # First: check local database.
    # --------------------------------------------------------

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        df = _load_city_data(
            conn,
            city_name,
        )

    finally:

        conn.close()

    if not df.empty:
        return df

    # --------------------------------------------------------
    # Second: city is not cached.
    # Fetch it dynamically.
    # --------------------------------------------------------

    _ingest_city(
        city_name
    )

    # --------------------------------------------------------
    # Third: load newly ingested data.
    # --------------------------------------------------------

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        return _load_city_data(
            conn,
            city_name,
        )

    finally:

        conn.close()


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    city = input(
        "Enter city name: "
    ).strip()

    try:

        df = get_city_data(
            city
        )

    except Exception as exc:

        print(
            f"\nError: {exc}"
        )

        raise SystemExit(1)

    print("=" * 60)
    print(
        "CityAir — Data Loader"
    )
    print("=" * 60)

    print(
        f"\nCity: {city}"
    )

    print(
        f"Rows loaded: {len(df)}"
    )

    if df.empty:

        print(
            "\nNo air-quality readings "
            "were found for this city "
            "or nearby monitoring stations."
        )

    else:

        print(
            "\nRaw Data Sample:"
        )

        print(
            df.head(10)
            .to_string(index=False)
        )