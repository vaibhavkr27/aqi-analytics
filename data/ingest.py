"""
CityAir — production-style OpenAQ ingestion pipeline.

The pipeline:

    city coordinates
        ↓
    OpenAQ locations
        ↓
    sensors
        ↓
    hourly measurements
        ↓
    SQLite

Usage:

    python data/ingest.py

The initial city list is stored in data/cities.py.
"""
from __future__ import annotations
from math import radians, sin, cos, sqrt, atan2
from geocoder import geocode_city


import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# Allow importing data.cities when running:
# python data/ingest.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))




# ============================================================
# Configuration
# ============================================================

API_KEY = os.getenv("OPENAQ_API_KEY")

BASE_URL = "https://api.openaq.org/v3"

DB_PATH = PROJECT_ROOT / "db" / "aqi.db"
SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"

LOOKBACK_DAYS = 30

LOCATION_RADIUS_METERS = 25_000

PARAMETERS_OF_INTEREST = {
    "pm25",
    "pm10",
    "no2",
    "o3",
    "so2",
    "co",
}

REQUEST_TIMEOUT = 30
REQUEST_DELAY_SECONDS = 0.25


# ============================================================
# API
# ============================================================

def api_get(
    path: str,
    params: dict | None = None,
) -> dict:

    if not API_KEY:
        raise RuntimeError(
            "OPENAQ_API_KEY is not configured."
        )

    response = requests.get(
        f"{BASE_URL}{path}",
        headers={
            "X-API-Key": API_KEY,
            "Accept": "application/json",
            "User-Agent": "CityAir/1.0",
        },
        params=params or {},
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    time.sleep(REQUEST_DELAY_SECONDS)

    return response.json()


# ============================================================
# Database
# ============================================================

def initialize_database(conn: sqlite3.Connection) -> None:

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        conn.executescript(file.read())

    conn.commit()


def get_or_create_city(
    conn: sqlite3.Connection,
    name: str,
    state: str | None,
    latitude: float,
    longitude: float,
    geocoder: str = "static",
) -> int:

    existing = conn.execute(
        """
        SELECT city_id
        FROM cities
        WHERE city_name = ?
        AND state IS ?
        """,
        (name, state),
    ).fetchone()

    if existing:
        return existing[0]

    cursor = conn.execute(
        """
        INSERT INTO cities (
            city_name,
            state,
            country,
            latitude,
            longitude,
            geocoder
        )
        VALUES (?, ?, 'India', ?, ?, ?)
        """,
        (
            name,
            state,
            latitude,
            longitude,
            geocoder,
        ),
    )

    conn.commit()

    return cursor.lastrowid


# ============================================================
# OpenAQ locations
# ============================================================

def find_locations(
    latitude: float,
    longitude: float,
) -> list[dict]:

    data = api_get(
        "/locations",
        {
            "coordinates": f"{latitude},{longitude}",
            "radius": LOCATION_RADIUS_METERS,
            "iso": "IN",
            "limit": 100,
            "page": 1,
        },
    )

    return data.get("results", [])


def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float,
) -> float:

    earth_radius_km = 6371.0

    lat1 = radians(latitude1)
    lat2 = radians(latitude2)

    delta_lat = radians(latitude2 - latitude1)
    delta_lon = radians(longitude2 - longitude1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


def choose_location(
    locations: list[dict],
    city_latitude: float,
    city_longitude: float,
    start: str,
    end: str,
) -> dict | None:

    if not locations:
        return None

    candidates = []

    for location in locations:

        coordinates = location.get("coordinates") or {}

        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")

        if latitude is None or longitude is None:
            continue

        distance = calculate_distance_km(
            city_latitude,
            city_longitude,
            latitude,
            longitude,
        )

        sensors = location.get("sensors") or []

        usable_sensors = []

        for sensor in sensors:

            parameter = sensor.get("parameter") or {}

            if not isinstance(parameter, dict):
                continue

            parameter_name = parameter.get("name")

            if parameter_name not in PARAMETERS_OF_INTEREST:
                continue

            try:
                measurements = get_hourly_measurements(
                    sensor["id"],
                    start,
                    end,
                )
            except requests.RequestException:
                continue

            if measurements:
                usable_sensors.append(
                    {
                        "sensor": sensor,
                        "readings": len(measurements),
                    }
                )

        if not usable_sensors:
            continue

        candidates.append(
            {
                "location": location,
                "distance": distance,
                "usable_sensors": usable_sensors,
            }
        )

    if not candidates:
        return None

    # Among stations that actually have data,
    # choose the nearest one.
    candidates.sort(
        key=lambda candidate: candidate["distance"]
    )

    selected = candidates[0]

    location = selected["location"]

    print(
        f"   Selected station: "
        f"{location.get('name')} "
        f"({selected['distance']:.2f} km away)"
    )

    print(
        f"   Usable sensors: "
        f"{len(selected['usable_sensors'])}"
    )

    return location

    if not locations:
        return None

    candidates = []

    for location in locations:

        coordinates = location.get("coordinates") or {}

        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")

        if latitude is None or longitude is None:
            continue

        sensors = location.get("sensors") or []

        useful_parameters = set()

        for sensor in sensors:

            parameter = sensor.get("parameter") or {}

            if isinstance(parameter, dict):

                name = parameter.get("name")

                if name in PARAMETERS_OF_INTEREST:
                    useful_parameters.add(name)

        distance = calculate_distance_km(
            city_latitude,
            city_longitude,
            latitude,
            longitude,
        )

        candidates.append(
            {
                "location": location,
                "distance": distance,
                "parameters": len(useful_parameters),
                "is_monitor": bool(location.get("isMonitor")),
                "is_mobile": bool(location.get("isMobile")),
            }
        )

    if not candidates:
        return None

    # Prefer stations with useful sensors.
    # Among those, choose the nearest station.
    candidates.sort(
        key=lambda item: (
            item["parameters"] == 0,
            item["distance"],
        )
    )

    return candidates[0]["location"]

def save_location(
    conn: sqlite3.Connection,
    city_id: int,
    location: dict,
) -> int:

    openaq_id = location["id"]

    coordinates = location.get("coordinates") or {}

    # OpenAQ can return datetime fields as nested objects.
    # Convert them into SQLite-friendly strings.
    datetime_first = location.get("datetimeFirst")
    datetime_last = location.get("datetimeLast")

    if isinstance(datetime_first, dict):
        datetime_first = (
            datetime_first.get("utc")
            or datetime_first.get("local")
        )

    if isinstance(datetime_last, dict):
        datetime_last = (
            datetime_last.get("utc")
            or datetime_last.get("local")
        )

    existing = conn.execute(
        """
        SELECT location_id
        FROM locations
        WHERE openaq_location_id = ?
        """,
        (openaq_id,),
    ).fetchone()

    if existing:

        conn.execute(
            """
            UPDATE locations
            SET
                city_id = ?,
                location_name = ?,
                latitude = ?,
                longitude = ?,
                is_mobile = ?,
                is_monitor = ?,
                first_measurement = ?,
                last_measurement = ?
            WHERE openaq_location_id = ?
            """,
            (
                city_id,
                location.get("name"),
                coordinates.get("latitude"),
                coordinates.get("longitude"),
                int(bool(location.get("isMobile"))),
                int(bool(location.get("isMonitor"))),
                datetime_first,
                datetime_last,
                openaq_id,
            ),
        )

        conn.commit()

        return existing[0]

    cursor = conn.execute(
        """
        INSERT INTO locations (
            city_id,
            openaq_location_id,
            location_name,
            latitude,
            longitude,
            is_mobile,
            is_monitor,
            first_measurement,
            last_measurement
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            city_id,
            openaq_id,
            location.get("name"),
            coordinates.get("latitude"),
            coordinates.get("longitude"),
            int(bool(location.get("isMobile"))),
            int(bool(location.get("isMonitor"))),
            datetime_first,
            datetime_last,
        ),
    )

    conn.commit()

    return cursor.lastrowid

# ============================================================
# Sensors
# ============================================================

def get_sensors(
    openaq_location_id: int,
) -> list[dict]:

    data = api_get(
        f"/locations/{openaq_location_id}/sensors",
        {
            "limit": 100,
            "page": 1,
        },
    )

    return data.get("results", [])


def save_sensor(
    conn: sqlite3.Connection,
    location_id: int,
    sensor: dict,
) -> int | None:

    parameter = sensor.get("parameter") or {}

    if not isinstance(parameter, dict):
        return None

    parameter_name = parameter.get("name")

    if parameter_name not in PARAMETERS_OF_INTEREST:
        return None

    openaq_sensor_id = sensor["id"]
    datetime_first = sensor.get("datetimeFirst")
    datetime_last = sensor.get("datetimeLast")

    if isinstance(datetime_first, dict):
      datetime_first = datetime_first.get("utc")

    if isinstance(datetime_last, dict):
      datetime_last = datetime_last.get("utc")

    existing = conn.execute(
        """
        SELECT sensor_id
        FROM sensors
        WHERE openaq_sensor_id = ?
        """,
        (openaq_sensor_id,),
    ).fetchone()

    if existing:

        conn.execute(
            """
            UPDATE sensors
            SET
                sensor_name = ?,
                parameter = ?,
                unit = ?,
                first_measurement = ?,
                last_measurement = ?
            WHERE openaq_sensor_id = ?
            """,
            (
                sensor.get("name"),
                parameter_name,
                parameter.get("units"),
                datetime_first,
                datetime_last,
                openaq_sensor_id,
            ),
        )

        conn.commit()

        return existing[0]

    cursor = conn.execute(
        """
        INSERT INTO sensors (
            location_id,
            openaq_sensor_id,
            sensor_name,
            parameter,
            unit,
            first_measurement,
            last_measurement
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            location_id,
            openaq_sensor_id,
            sensor.get("name"),
            parameter_name,
            parameter.get("units"),
            datetime_first,
            datetime_last,
        ),
    )

    conn.commit()

    return cursor.lastrowid


# ============================================================
# Measurements
# ============================================================

def get_hourly_measurements(
    sensor_id: int,
    start: str,
    end: str,
) -> list[dict]:

    data = api_get(
        f"/sensors/{sensor_id}/hours",
        {
            "datetime_from": start,
            "datetime_to": end,
            "limit": 1000,
            "page": 1,
        },
    )

    return data.get("results", [])


def insert_measurements(
    conn: sqlite3.Connection,
    city_id: int,
    sensor_id: int,
    parameter: str,
    unit: str | None,
    measurements: list[dict],
) -> int:

    inserted = 0

    for measurement in measurements:

        value = measurement.get("value")

        if value is None:
            continue

        try:
            value = float(value)
        except (TypeError, ValueError):
            continue

        if value < 0:
            continue

        period = measurement.get("period") or {}

        timestamp = (
            period.get("datetimeTo") or {}
        ).get("utc")

        if not timestamp:
            continue

        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO readings (
                sensor_id,
                city_id,
                parameter,
                value,
                unit,
                measured_at,
                source,
                ingested_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sensor_id,
                city_id,
                parameter,
                value,
                unit,
                timestamp,
                "openaq",
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        inserted += cursor.rowcount

    conn.commit()

    return inserted


# ============================================================
# City ingestion
# ============================================================

def ingest_city(
    conn: sqlite3.Connection,
    city_name: str,
    city: dict,
    start: str,
    end: str,
) -> dict:

    result = {
        "city": city_name,
        "locations": 0,
        "sensors": 0,
        "readings": 0,
        "status": "success",
    }

    city_id = get_or_create_city(
        conn,
        city_name,
        city["state"],
        city["latitude"],
        city["longitude"],
    )

    try:

        locations = find_locations(
            city["latitude"],
            city["longitude"],
        )

    except requests.RequestException as exc:

        result["status"] = f"location_error: {exc}"

        return result

    if not locations:

        result["status"] = "no_monitoring_station"

        return result

    # We intentionally choose the best available station rather
    # than averaging arbitrary stations together.
    location = choose_location(
        locations,
        city["latitude"],
        city["longitude"],
        start,
        end,
    )

    if not location:
        result["status"] = "no_monitoring_station_with_data"
        return result

    location_id = save_location(
        conn,
        city_id,
        location,
    )

    result["locations"] = 1

    try:

        sensors = get_sensors(
            location["id"]
        )

    except requests.RequestException as exc:

        result["status"] = f"sensor_error: {exc}"

        return result

    for sensor in sensors:

        parameter = (
            sensor.get("parameter") or {}
        ).get("name")

        if parameter not in PARAMETERS_OF_INTEREST:
            continue

        sensor_id = save_sensor(
            conn,
            location_id,
            sensor,
        )

        if sensor_id is None:
            continue

        result["sensors"] += 1

        try:

            measurements = get_hourly_measurements(
                sensor["id"],
                start,
                end,
            )

        except requests.RequestException:

            continue

        result["readings"] += insert_measurements(
            conn,
            city_id,
            sensor_id,
            parameter,
            (
                sensor.get("parameter") or {}
            ).get("units"),
            measurements,
        )

    return result


# ============================================================
# Main
# ============================================================

def main(city_name: str) -> None:

    if not API_KEY:
        raise SystemExit(
            "ERROR: OPENAQ_API_KEY is not set."
        )

    now = datetime.now(timezone.utc)

    start = (
        now - timedelta(days=LOOKBACK_DAYS)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    end = now.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    print()
    print("==============================================")
    print("CityAir — Data Ingestion")
    print("==============================================")
    print(f"City: {city_name}")
    print(f"Period: {start} → {end}")
    print()

    # --------------------------------------------------------
    # Resolve city name → coordinates using geocoder
    # --------------------------------------------------------

    print(f"Searching for {city_name}...")

    city = geocode_city(city_name)

    if not city:
        raise SystemExit(
            f"ERROR: Could not find '{city_name}'."
        )

    print(
        f"Found: {city['city']}, "
        f"{city.get('state', '')}, "
        f"{city.get('country', '')}"
    )

    print(
        f"Coordinates: "
        f"{city['latitude']}, {city['longitude']}"
    )

    conn = sqlite3.connect(DB_PATH)

    try:

        initialize_database(conn)

        print()
        print(f"→ Ingesting {city['city']}")

        result = ingest_city(
            conn,
            city["city"],
            city,
            start,
            end,
        )

        print(
            f"   locations={result['locations']} "
            f"sensors={result['sensors']} "
            f"new_readings={result['readings']} "
            f"status={result['status']}"
        )

        print()
        print("==============================================")
        print("Ingestion complete")
        print("==============================================")
        print(
            f"Locations : {result['locations']}"
        )
        print(
            f"Sensors   : {result['sensors']}"
        )
        print(
            f"Readings  : {result['readings']}"
        )
        print(
            f"Database  : {DB_PATH}"
        )

    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python data/ingest.py <city_name>\n"
            "Example: python data/ingest.py Delhi"
        )

    main(" ".join(sys.argv[1:]))