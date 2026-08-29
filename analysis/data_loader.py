from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd


# ============================================================
# Database configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DB_PATH = PROJECT_DIR / "db" / "aqi.db"


# ============================================================
# Load city readings
# ============================================================

def get_city_data(
    city_name: str,
) -> pd.DataFrame:
    """
    Load raw AQI readings for the requested city.

    The city name comes from the user.
    SQL/database access is kept inside this module.
    """

    conn = sqlite3.connect(DB_PATH)

    try:

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

        df = pd.read_sql_query(
            query,
            conn,
            params=(city_name,),
        )

    finally:
        conn.close()

    return df


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    city = input(
        "Enter city name: "
    ).strip()

    df = get_city_data(city)

    print("=" * 60)
    print("CityAir — Data Loader")
    print("=" * 60)

    print(
        f"\nCity: {city}"
    )

    print(
        f"Rows loaded: {len(df)}"
    )

    if df.empty:

        print(
            "\nNo readings found for this city."
        )

    else:

        print(
            "\nRaw Data Sample:"
        )

        print(
            df.head(10)
            .to_string(index=False)
        )