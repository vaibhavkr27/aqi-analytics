"""
CityAir — Pandas Analytics

Takes the processed DataFrame from processor.py and generates
a complete 30-day analytical report for a city.
"""

from __future__ import annotations


from typing import Any
from pathlib import Path
import pandas as pd









# ============================================================
# Constants
# ============================================================

PARAMETER_LABELS = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "no2": "NO₂",
    "so2": "SO₂",
    "co": "CO",
    "o3": "O₃",
}


def parameter_label(parameter: str) -> str:
    """Return a user-friendly pollutant name."""

    return PARAMETER_LABELS.get(
        parameter,
        parameter.upper(),
    )

# ============================================================
# Indian AQI / CPCB configuration
# ============================================================

AQI_BREAKPOINTS = {
    "pm25": [
        (0.0, 30.0, 0, 50),
        (30.0, 60.0, 51, 100),
        (60.0, 90.0, 101, 200),
        (90.0, 120.0, 201, 300),
        (120.0, 250.0, 301, 400),
        (250.0, float("inf"), 401, 500),
    ],
    "pm10": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 250.0, 101, 200),
        (250.0, 350.0, 201, 300),
        (350.0, 430.0, 301, 400),
        (430.0, float("inf"), 401, 500),
    ],
    "no2": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 180.0, 101, 200),
        (180.0, 280.0, 201, 300),
        (280.0, 400.0, 301, 400),
        (400.0, float("inf"), 401, 500),
    ],
    "o3": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 168.0, 101, 200),
        (168.0, 208.0, 201, 300),
        (208.0, 748.0, 301, 400),
        (748.0, float("inf"), 401, 500),
    ],
    "so2": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 380.0, 101, 200),
        (380.0, 800.0, 201, 300),
        (800.0, 1600.0, 301, 400),
        (1600.0, float("inf"), 401, 500),
    ],
    "co": [
        (0.0, 1.0, 0, 50),
        (1.0, 2.0, 51, 100),
        (2.0, 10.0, 101, 200),
        (10.0, 17.0, 201, 300),
        (17.0, 34.0, 301, 400),
        (34.0, float("inf"), 401, 500),
    ],
}


AQI_AVERAGING_HOURS = {
    "pm25": 24,
    "pm10": 24,
    "no2": 24,
    "so2": 24,
    "o3": 8,
    "co": 8,
}


AQI_UNITS = {
    "pm25": "µg/m³",
    "pm10": "µg/m³",
    "no2": "µg/m³",
    "so2": "µg/m³",
    "o3": "µg/m³",
    "co": "mg/m³",
}


AQI_CATEGORIES = [
    (0, 50, "Good"),
    (51, 100, "Satisfactory"),
    (101, 200, "Moderate"),
    (201, 300, "Poor"),
    (301, 400, "Very Poor"),
    (401, 500, "Severe"),
]



def get_aqi_category(
    aqi: float,
) -> str:
    """Return the Indian/CPCB AQI category."""

    for lower, upper, category in AQI_CATEGORIES:
        if lower <= aqi <= upper:
            return category

    if aqi > 500:
        return "Severe"

    return "Good"




def calculate_aqi_subindex(
    parameter: str,
    concentration: float,
) -> float | None:
    """
    Calculate a pollutant AQI sub-index using
    CPCB breakpoint interpolation.
    """

    if parameter not in AQI_BREAKPOINTS:
        return None

    if concentration is None:
        return None

    concentration = float(
        concentration
    )

    if concentration < 0:
        return None

    for (
        concentration_low,
        concentration_high,
        aqi_low,
        aqi_high,
    ) in AQI_BREAKPOINTS[parameter]:

        if (
            concentration >= concentration_low
            and concentration <= concentration_high
        ):

            if concentration_high == float("inf"):
                return 500.0

            subindex = (
                (
                    (aqi_high - aqi_low)
                    /
                    (
                        concentration_high
                        - concentration_low
                    )
                )
                *
                (
                    concentration
                    - concentration_low
                )
                + aqi_low
            )

            return round(
                min(500.0, max(0.0, subindex)),
                1,
            )

    return None


def get_latest_aqi_average(
    df: pd.DataFrame,
    parameter: str,
) -> dict[str, Any] | None:
    """
    Calculate the latest rolling average required
    for the pollutant AQI sub-index.
    """

    if parameter not in AQI_AVERAGING_HOURS:
        return None

    parameter_df = df[
        df["parameter"] == parameter
    ].copy()

    if parameter_df.empty:
        return None

    parameter_df = parameter_df[
        [
            "measured_at_ist",
            "value_standardized",
        ]
    ].dropna(
        subset=[
            "measured_at_ist",
            "value_standardized",
        ]
    )

    if parameter_df.empty:
        return None

    # Multiple readings within the same hour
    # are reduced to one hourly mean.
    hourly = (
        parameter_df
        .set_index("measured_at_ist")
        .resample("1h")["value_standardized"]
        .mean()
        .dropna()
    )

    if hourly.empty:
        return None

    averaging_hours = AQI_AVERAGING_HOURS[
        parameter
    ]

    # Require a complete averaging window.
    rolling = (
        hourly
        .rolling(
            window=averaging_hours,
            min_periods=averaging_hours,
        )
        .mean()
        .dropna()
    )

    if rolling.empty:
        return None

    latest_timestamp = rolling.index[-1]

    latest_average = float(
        rolling.iloc[-1]
    )

    window_start = (
        latest_timestamp
        - pd.Timedelta(
            hours=averaging_hours - 1
        )
    )

    window = hourly.loc[
        window_start:latest_timestamp
    ]

    observation_count = int(
        window.notna().sum()
    )

    return {
        "average": latest_average,
        "timestamp": str(
            latest_timestamp
        ),
        "observations": observation_count,
        "averaging_hours": averaging_hours,
    }

def calculate_aqi_subindices(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """
    Calculate available pollutant AQI sub-indices.
    """

    results = []

    for parameter in AQI_AVERAGING_HOURS:

        latest = get_latest_aqi_average(
            df,
            parameter,
        )

        if latest is None:
            continue

        # CPCB AQI calculation requires at least
        # 16 observations for a pollutant.
        if latest["observations"] < 16:

            results.append(
                {
                    "parameter": parameter,
                    "label": PARAMETER_LABELS.get(
                        parameter,
                        parameter.upper(),
                    ),
                    "status": "insufficient_data",
                    "reason": (
                        "Fewer than 16 observations "
                        "available."
                    ),
                    "observations": latest[
                        "observations"
                    ],
                    "averaging_hours": latest[
                        "averaging_hours"
                    ],
                }
            )

            continue

        concentration = latest[
            "average"
        ]

        subindex = calculate_aqi_subindex(
            parameter,
            concentration,
        )

        if subindex is None:
            continue

        results.append(
            {
                "parameter": parameter,
                "label": PARAMETER_LABELS.get(
                    parameter,
                    parameter.upper(),
                ),
                "status": "valid",
                "concentration": round(
                    concentration,
                    3,
                ),
                "unit": AQI_UNITS[
                    parameter
                ],
                "sub_index": subindex,
                "category": get_aqi_category(
                    subindex
                ),
                "averaging_hours": latest[
                    "averaging_hours"
                ],
                "observations": latest[
                    "observations"
                ],
                "timestamp": latest[
                    "timestamp"
                ],
            }
        )

    return results



def calculate_overall_aqi(
    subindices: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate the overall city-level AQI.

    The highest pollutant sub-index determines
    the overall AQI.
    """

    valid = [
        item
        for item in subindices
        if item.get("status") == "valid"
    ]

    parameters = {
        item["parameter"]
        for item in valid
    }

    has_required_particulate_pollutant = (
        "pm25" in parameters
        or "pm10" in parameters
    )

    if (
        len(valid) < 3
        or not has_required_particulate_pollutant
    ):

        return {
            "status": "insufficient_data",
            "aqi": None,
            "category": None,
            "dominant_pollutant": None,
            "dominant_pollutant_label": None,
            "reason": (
                "Overall AQI requires at least "
                "3 pollutants, including PM2.5 "
                "or PM10."
            ),
        }

    dominant = max(
        valid,
        key=lambda item: item["sub_index"],
    )

    aqi = int(
        round(
            dominant["sub_index"]
        )
    )

    aqi = max(
        0,
        min(
            500,
            aqi,
        ),
    )

    return {
        "status": "valid",
        "aqi": aqi,
        "category": get_aqi_category(aqi),
        "dominant_pollutant": dominant[
            "parameter"
        ],
        "dominant_pollutant_label": dominant[
            "label"
        ],
    }



def calculate_city_aqi(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Calculate the complete Indian AQI analysis
    for the selected city.
    """

    if df.empty:
        return {
            "status": "no_data",
            "aqi": None,
            "category": None,
            "dominant_pollutant": None,
            "dominant_pollutant_label": None,
            "subindices": [],
        }

    subindices = calculate_aqi_subindices(
        df
    )

    overall = calculate_overall_aqi(
        subindices
    )

    return {
        **overall,
        "subindices": subindices,
    }




# ============================================================
# 1. 30-Day Pollutant Statistics
# ============================================================

def get_pollutant_statistics(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:

    if df.empty:
        return []

    grouped = (
        df.groupby("parameter")[
            "value_standardized"
        ]
        .agg(
            [
                "count",
                "mean",
                "median",
                "min",
                "max",
                "std",
            ]
        )
        .reset_index()
    )

    result = []

    for _, row in grouped.iterrows():

        values = df[
            df["parameter"]
            == row["parameter"]
        ]["value_standardized"]

        result.append(
            {
                "parameter": row["parameter"],
                "observations": int(row["count"]),
                "average": round(
                    float(row["mean"]),
                    2,
                ),
                "median": round(
                    float(row["median"]),
                    2,
                ),
                "minimum": round(
                    float(row["min"]),
                    2,
                ),
                "maximum": round(
                    float(row["max"]),
                    2,
                ),
                "standard_deviation": round(
                    float(row["std"])
                    if not pd.isna(row["std"])
                    else 0,
                    2,
                ),
                "p95": round(
                    float(
                        values.quantile(
                            0.95
                        )
                    ),
                    2,
                ),
                "p99": round(
                    float(
                        values.quantile(
                            0.99
                        )
                    ),
                    2,
                ),
            }
        )

    return result


# ============================================================
# 2. Daily Trends
# ============================================================

def get_daily_trends(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:

    if df.empty:
        return []

    daily = (
        df.groupby(
            [
                "date",
                "parameter",
            ]
        )["value_standardized"]
        .agg(
            [
                "mean",
                "min",
                "max",
                "count",
            ]
        )
        .reset_index()
    )

    result = []

    for _, row in daily.iterrows():

        result.append(
            {
                "day": str(row["date"]),
                "parameter": row["parameter"],
                "average": round(
                    float(row["mean"]),
                    2,
                ),
                "minimum": round(
                    float(row["min"]),
                    2,
                ),
                "maximum": round(
                    float(row["max"]),
                    2,
                ),
                "observations": int(
                    row["count"]
                ),
            }
        )

    return result


# ============================================================
# 3. Hourly Patterns — IST
# ============================================================

def get_hourly_patterns(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:

    if df.empty:
        return []

    hourly = (
        df.groupby(
            [
                "hour",
                "parameter",
            ]
        )["value_standardized"]
        .agg(
            [
                "mean",
                "min",
                "max",
                "count",
            ]
        )
        .reset_index()
    )

    hourly = hourly.sort_values(
        [
            "hour",
            "parameter",
        ]
    )

    result = []

    for _, row in hourly.iterrows():

        result.append(
            {
                "hour_ist": f"{int(row['hour']):02d}",
                "parameter": row["parameter"],
                "average": round(
                    float(row["mean"]),
                    2,
                ),
                "minimum": round(
                    float(row["min"]),
                    2,
                ),
                "maximum": round(
                    float(row["max"]),
                    2,
                ),
                "observations": int(
                    row["count"]
                ),
            }
        )

    return result


# ============================================================
# 4. Weekday / Weekend Analysis
# ============================================================

def get_weekday_weekend_analysis(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:

    if df.empty:
        return []

    temp = df.copy()

    temp["day_type"] = temp[
        "day_of_week"
    ].isin(
        [
            "Saturday",
            "Sunday",
        ]
    )

    temp["day_type"] = temp[
        "day_type"
    ].map(
        {
            True: "weekend",
            False: "weekday",
        }
    )

    grouped = (
        temp.groupby(
            [
                "day_type",
                "parameter",
            ]
        )["value_standardized"]
        .agg(
            [
                "mean",
                "min",
                "max",
                "count",
            ]
        )
        .reset_index()
    )

    result = []

    for _, row in grouped.iterrows():

        result.append(
            {
                "day_type": row[
                    "day_type"
                ],
                "parameter": row[
                    "parameter"
                ],
                "average": round(
                    float(row["mean"]),
                    2,
                ),
                "minimum": round(
                    float(row["min"]),
                    2,
                ),
                "maximum": round(
                    float(row["max"]),
                    2,
                ),
                "observations": int(
                    row["count"]
                ),
            }
        )

    return result


# ============================================================
# 5. Day-of-Week Analysis
# ============================================================

def get_day_of_week_analysis(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:

    if df.empty:
        return []

    grouped = (
        df.groupby(
            [
                "day_of_week_num",
                "day_of_week",
                "parameter",
            ]
        )["value_standardized"]
        .mean()
        .reset_index(
            name="average"
        )
    )

    grouped = grouped.sort_values(
        [
            "day_of_week_num",
            "parameter",
        ]
    )

    result = []

    for _, row in grouped.iterrows():

        result.append(
            {
                "day_of_week": row[
                    "day_of_week"
                ],
                "parameter": row[
                    "parameter"
                ],
                "average": round(
                    float(row["average"]),
                    2,
                ),
            }
        )

    return result


# ============================================================
# 6. Pollutant Correlation
# ============================================================

def get_pollutant_correlations(
    df: pd.DataFrame,
) -> dict[str, dict[str, float]]:

    if df.empty:
        return {}

    pivot = (
        df.pivot_table(
            index="measured_at_ist",
            columns="parameter",
            values="value_standardized",
            aggfunc="mean",
        )
    )

    if pivot.empty:
        return {}

    correlation = pivot.corr()

    correlation = correlation.round(
        3
    )

    return correlation.to_dict()


# ============================================================
# 7. Pollution Peaks
# ============================================================

def get_pollution_peaks(
    df: pd.DataFrame,
    top_n: int = 10,
) -> list[dict[str, Any]]:

    if df.empty:
        return []

    peaks = (
        df[
            [
                "measured_at_ist",
                "parameter",
                "value_standardized",
                "standardized_unit",
            ]
        ]
        .sort_values(
            "value_standardized",
            ascending=False,
        )
        .head(top_n)
    )

    result = []

    for _, row in peaks.iterrows():

        result.append(
            {
                "timestamp": str(
                    row[
                        "measured_at_ist"
                    ]
                ),
                "parameter": row[
                    "parameter"
                ],
                "value": round(
                    float(
                        row[
                            "value_standardized"
                        ]
                    ),
                    2,
                ),
                "unit": row[
                    "standardized_unit"
                ],
            }
        )

    return result


# ============================================================
# 8. Statistical Anomalies
# ============================================================

def get_anomalies(
    df: pd.DataFrame,
    top_n: int = 20,
) -> list[dict[str, Any]]:

    if df.empty:
        return []

    if (
        "is_statistical_anomaly"
        not in df.columns
    ):
        return []

    anomalies = df[
        df["is_statistical_anomaly"]
    ].copy()

    if anomalies.empty:
        return []

    anomalies["_severity"] = (
        anomalies[
            "robust_z_score"
        ]
        .abs()
        .fillna(0)
    )

    anomalies = anomalies.sort_values(
        "_severity",
        ascending=False,
    )

    result = []

    for _, row in anomalies.head(
        top_n
    ).iterrows():

        result.append(
            {
                "timestamp": str(
                    row[
                        "measured_at_ist"
                    ]
                ),
                "parameter": row[
                    "parameter"
                ],
                "value": round(
                    float(
                        row[
                            "value_standardized"
                        ]
                    ),
                    2,
                ),
                "unit": row[
                    "standardized_unit"
                ],
                "local_median": (
                    None
                    if pd.isna(
                        row[
                            "local_median"
                        ]
                    )
                    else round(
                        float(
                            row[
                                "local_median"
                            ]
                        ),
                        2,
                    )
                ),
                "deviation_percent": (
                    None
                    if pd.isna(
                        row[
                            "deviation_percent"
                        ]
                    )
                    else round(
                        float(
                            row[
                                "deviation_percent"
                            ]
                        ),
                        2,
                    )
                ),
                "robust_z_score": (
                    None
                    if pd.isna(
                        row[
                            "robust_z_score"
                        ]
                    )
                    else round(
                        float(
                            row[
                                "robust_z_score"
                            ]
                        ),
                        2,
                    )
                ),
            }
        )

    return result


# ============================================================
# 9. Daily Extremes
# ============================================================

def get_daily_extremes(
    df: pd.DataFrame,
    parameter: str = "pm25",
) -> dict[str, Any] | None:

    if df.empty:
        return None

    parameter_df = df[
        df["parameter"] == parameter
    ]

    if parameter_df.empty:
        return None

    daily = (
        parameter_df
        .groupby("date")[
            "value_standardized"
        ]
        .mean()
        .dropna()
    )

    if daily.empty:
        return None

    highest_day = daily.idxmax()
    lowest_day = daily.idxmin()

    return {
        "parameter": parameter,
        "highest_day": str(
            highest_day
        ),
        "highest_average": round(
            float(
                daily.loc[
                    highest_day
                ]
            ),
            2,
        ),
        "lowest_day": str(
            lowest_day
        ),
        "lowest_average": round(
            float(
                daily.loc[
                    lowest_day
                ]
            ),
            2,
        ),
    }


# ============================================================
# 10. Hourly Extremes
# ============================================================

def get_hourly_extremes(
    df: pd.DataFrame,
    parameter: str = "pm25",
) -> dict[str, Any] | None:

    if df.empty:
        return None

    parameter_df = df[
        df["parameter"] == parameter
    ]

    if parameter_df.empty:
        return None

    hourly = (
        parameter_df
        .groupby("hour")[
            "value_standardized"
        ]
        .mean()
        .dropna()
    )

    if hourly.empty:
        return None

    highest_hour = hourly.idxmax()
    lowest_hour = hourly.idxmin()

    return {
        "parameter": parameter,
        "highest_hour_ist": (
            f"{int(highest_hour):02d}:00"
        ),
        "highest_average": round(
            float(
                hourly.loc[
                    highest_hour
                ]
            ),
            2,
        ),
        "lowest_hour_ist": (
            f"{int(lowest_hour):02d}:00"
        ),
        "lowest_average": round(
            float(
                hourly.loc[
                    lowest_hour
                ]
            ),
            2,
        ),
    }


# ============================================================
# 11. Data Coverage
# ============================================================

def get_data_coverage(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:

    if df.empty:
        return []

    result = []

    for parameter, group in df.groupby(
        "parameter"
    ):

        result.append(
            {
                "parameter": parameter,
                "observations": int(
                    len(group)
                ),
                "days_available": int(
                    group["date"]
                    .nunique()
                ),
                "hours_available": int(
                    group["hour"]
                    .nunique()
                ),
                "first_reading": str(
                    group[
                        "measured_at"
                    ].min()
                ),
                "last_reading": str(
                    group[
                        "measured_at"
                    ].max()
                ),
            }
        )

    return result


# ============================================================
# 12. Complete City Report
# ============================================================

def get_city_analytics(
    df: pd.DataFrame,
    city_name: str,
) -> dict[str, Any]:

    if df.empty:
        return {
            "city": city_name,

            "aqi": {
                "status": "no_data",
                "aqi": None,
                "category": None,
                "dominant_pollutant": None,
                "dominant_pollutant_label": None,
                "subindices": [],
            },

            "pollutant_statistics": [],
            "daily_trends": [],
            "hourly_patterns": [],
            "weekday_weekend": [],
            "day_of_week": [],
            "correlations": {},
            "pollution_peaks": [],
            "anomalies": [],
            "data_coverage": [],
            "daily_extremes": {},
            "hourly_extremes": {},
        }

    return {
        "city": city_name,

        "aqi": calculate_city_aqi(
            df
        ),

        "pollutant_statistics":
            get_pollutant_statistics(
                df
            ),

        "daily_trends":
            get_daily_trends(
                df
            ),

        "hourly_patterns":
            get_hourly_patterns(
                df
            ),

        "weekday_weekend":
            get_weekday_weekend_analysis(
                df
            ),

        "day_of_week":
            get_day_of_week_analysis(
                df
            ),

        "correlations":
            get_pollutant_correlations(
                df
            ),

        "pollution_peaks":
            get_pollution_peaks(
                df
            ),

        "anomalies":
            get_anomalies(
                df
            ),

        "data_coverage":
            get_data_coverage(
                df
            ),

        "daily_extremes":
            get_daily_extremes(
                df,
                "pm25",
            ),

        "hourly_extremes":
            get_hourly_extremes(
                df,
                "pm25",
            ),
    }

# ============================================================
# Main Test
# ============================================================

if __name__ == "__main__":

    import sqlite3

    city = "Mumbai"

    DB_PATH = (
        Path(__file__).resolve().parent.parent
        / "db"
        / "aqi.db"
    )

    conn = sqlite3.connect(DB_PATH)

    try:

        raw_readings = conn.execute("""
            SELECT
                r.measured_at,
                r.parameter,
                r.value,
                r.unit
            FROM readings r
            JOIN cities c
                ON c.city_id = r.city_id
            WHERE c.city_name = ?
            ORDER BY r.measured_at
        """, (city,)).fetchall()

    finally:
        conn.close()

    raw_df = pd.DataFrame(
        raw_readings,
        columns=[
            "measured_at",
            "parameter",
            "value",
            "unit",
        ],
    )

    from processor import process_city_data

    processed_df = process_city_data(
        raw_df
    )

    report = get_city_analytics(
        processed_df,
        city,
    )

    # ----------------------------------------------------
    # Pollutant statistics
    # ----------------------------------------------------

    print(
        "\n30-DAY POLLUTANT STATISTICS"
    )

    print(
        "-" * 60
    )

    for item in report[
        "pollutant_statistics"
    ]:
        print(item)

    # ----------------------------------------------------
    # Daily trends
    # ----------------------------------------------------

    print(
        "\nDAILY TRENDS"
    )

    print(
        "-" * 60
    )

    daily = report[
        "daily_trends"
    ]

    for item in daily[:15]:
        print(item)

    print(
        f"\nTotal daily records: "
        f"{len(daily)}"
    )

    # ----------------------------------------------------
    # Hourly patterns
    # ----------------------------------------------------

    print(
        "\nHOURLY PATTERNS — IST"
    )

    print(
        "-" * 60
    )

    hourly = report[
        "hourly_patterns"
    ]

    for item in hourly[:15]:
        print(item)

        print(
            f"\nTotal hourly groups: "
            f"{len(hourly)}"
        )

        # ----------------------------------------------------
        # Weekday / weekend
        # ----------------------------------------------------

        print(
            "\nWEEKDAY VS WEEKEND"
        )

        print(
            "-" * 60
        )

        for item in report[
            "weekday_weekend"
        ]:
            print(item)

        # ----------------------------------------------------
        # Day of week
        # ----------------------------------------------------

        print(
            "\nDAY OF WEEK ANALYSIS"
        )

        print(
            "-" * 60
        )

        for item in report[
            "day_of_week"
        ][:20]:
            print(item)

        # ----------------------------------------------------
        # Correlations
        # ----------------------------------------------------

        print(
            "\nPOLLUTANT CORRELATIONS"
        )

        print(
            "-" * 60
        )

        for parameter, values in report[
            "correlations"
        ].items():

            print(
                parameter,
                values,
            )

        # ----------------------------------------------------
        # Pollution peaks
        # ----------------------------------------------------

        print(
            "\nTOP POLLUTION PEAKS"
        )

        print(
            "-" * 60
        )

        for item in report[
            "pollution_peaks"
        ]:
            print(item)

        # ----------------------------------------------------
        # Anomalies
        # ----------------------------------------------------

        print(
            "\nSTATISTICAL ANOMALIES"
        )

        print(
            "-" * 60
        )

        anomalies = report[
            "anomalies"
        ]

        print(
            f"Total anomalies: "
            f"{len(anomalies)}"
        )

        for item in anomalies[:20]:
            print(item)

        # ----------------------------------------------------
        # Data coverage
        # ----------------------------------------------------

        print(
            "\nDATA COVERAGE"
        )

        print(
            "-" * 60
        )

        for item in report[
            "data_coverage"
        ]:
            print(item)

        # ----------------------------------------------------
        # PM2.5 extremes
        # ----------------------------------------------------

        print(
            "\nPM2.5 DAILY EXTREMES"
        )

        print(
            "-" * 60
        )

        print(
            report[
                "daily_extremes"
            ]
        )

        print(
            "\nPM2.5 HOURLY EXTREMES"
        )

        print(
            "-" * 60
        )

        print(
            report[
                "hourly_extremes"
            ]
        )

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        print(
            "\n"
            + "=" * 60
        )

        print(
            "ANALYTICS COMPLETE"
        )

        print(
            "=" * 60
        )

        print(
            "Processed rows:",
            len(processed_df),
        )

        print(
            "Pollutants:",
            len(
                report[
                    "pollutant_statistics"
                ]
            ),
        )

        print(
            "Daily records:",
            len(
                report[
                    "daily_trends"
                ]
            ),
        )

        print(
            "Hourly groups:",
            len(
                report[
                    "hourly_patterns"
                ]
            ),
        )

        print(
            "Anomalies:",
            len(
                report[
                    "anomalies"
                ]
            ),
        )



     