"""
CityAir geocoding service.

Uses OpenStreetMap Nominatim to convert an Indian city name
into geographic coordinates.

Nominatim public usage policy requires a descriptive User-Agent
and discourages high-frequency requests, so this module performs
explicit searches rather than autocomplete.
"""

from __future__ import annotations

from typing import Optional

import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "CityAir-Air-Quality-Analytics/1.0",
    "Accept": "application/json",
}


def geocode_city(city: str) -> Optional[dict]:
    """
    Search for an Indian city.

    Returns:
        {
            "display_name": ...,
            "city": ...,
            "state": ...,
            "country": ...,
            "latitude": ...,
            "longitude": ...
        }

    Returns None if no suitable result is found.
    """

    city = city.strip()

    if not city:
        return None

    params = {
        "q": f"{city}, India",
        "format": "jsonv2",
        "limit": 5,
        "countrycodes": "in",
        "addressdetails": 1,
    }

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=HEADERS,
        timeout=15,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    # Prefer actual populated places over generic geographic objects.
    preferred = [
        result
        for result in results
        if result.get("type") in {
            "city",
            "town",
            "municipality",
            "village",
            "suburb",
        }
    ]

    result = preferred[0] if preferred else results[0]

    address = result.get("address", {})

    return {
        "display_name": result.get("display_name", city),
        "city": (
            address.get("city")
            or address.get("town")
            or address.get("municipality")
            or address.get("village")
            or city
        ),
        "state": address.get("state"),
        "country": address.get("country", "India"),
        "latitude": float(result["lat"]),
        "longitude": float(result["lon"]),
    }