"""
CityAir — FastAPI Application

Receives a city from the frontend and returns
the complete AQI analysis report.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# Project path configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Make the project root available for imports.
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_DIR),
    )


# ============================================================
# Application imports
# ============================================================

from analysis.report import generate_city_report


# ============================================================
# FastAPI application
# ============================================================

app = FastAPI(
    title="CityAir API",
    description=(
        "City-based air quality and AQI "
        "analysis API."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

# Development origins.
#
# These allow the React frontend running on common
# development ports to communicate with FastAPI.

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ============================================================
# Health check
# ============================================================

@app.get("/")
def root() -> dict[str, str]:
    """
    Basic API health endpoint.
    """

    return {
        "service": "CityAir API",
        "status": "running",
    }


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """
    Health check used by the frontend or deployment system.
    """

    return {
        "status": "healthy",
    }


# ============================================================
# City report endpoint
# ============================================================

@app.get("/api/report")
def get_city_report(
    city: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description=(
            "City name entered by the user."
        ),
    ),
):
    """
    Generate the complete AQI report for
    the requested city.
    """

    city = city.strip()

    if not city:
        raise HTTPException(
            status_code=400,
            detail="City name cannot be empty.",
        )

    report = generate_city_report(
        city
    )

    # generate_city_report() already handles
    # the case where no data exists.
    if "error" in report:

        raise HTTPException(
            status_code=404,
            detail=report["error"],
        )

    return report