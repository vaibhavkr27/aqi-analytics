"""
CityAir — Pandas Analytics

Takes the processed DataFrame from processor.py and generates
a complete 30-day analytical report for a city.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DB_PATH = PROJECT_DIR / "db" / "aqi.db"


# ============================================================
# Import processor
# ============================================================

from processor import process_city_data


# ============================================================
# Constants
# ============================================================

PARAMETER_LABELS = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "no2": "NO₂",
    "so2": "SO₂",
    "co": "CO",
}


def parameter_label(parameter: str) -> str:
    """Return a user-friendly pollutant name."""

    return PARAMETER_LABELS.get(
        parameter,
        parameter.upper(),
    )


# ============================================================
# Load processed data
# ============================================================

def load_processed_data(
    conn: sqlite3.Connection,
    city_name: str,
) -> pd.DataFrame:
    """
    Load raw city readings through processor.py.

    processor.py handles:
    - cleaning
    - timezone conversion
    - unit normalization
    - anomaly detection
    - date/time features
    """

    df = process_city_data(
        conn,
        city_name,
    )

    if df is None:
        return pd.DataFrame()

    return df.copy()


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
    conn: sqlite3.Connection,
    city_name: str,
) -> dict[str, Any]:
    """
    Generate the complete analytical report for a city.
    """

    df = load_processed_data(
        conn,
        city_name,
    )

    if df.empty:
        return {
            "city": city_name,
            "raw_readings": [],
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

        "raw_readings": (
            df.to_dict(
                orient="records"
            )
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

    city = "Mumbai"

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "CityAir — Pandas Analytics"
        )

        print(
            "=" * 60
        )

        print(
            f"City: {city}"
        )

        print(
            "=" * 60
        )

        report = get_city_analytics(
            conn,
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
            "Raw readings:",
            len(
                report[
                    "raw_readings"
                ]
            ),
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

    finally:

        conn.close()