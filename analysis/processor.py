from pathlib import Path
import sys

import pandas as pd


# ============================================================
# Import analytics functions
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

sys.path.insert(0, str(PROJECT_DIR))

# ============================================================
# Load raw city data


# ============================================================
# Basic cleaning and feature engineering
# ============================================================

def prepare_data(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return df

    df = df.copy()

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    df["measured_at"] = pd.to_datetime(
        df["measured_at"],
        utc=True,
        errors="coerce",
    )

    # Remove rows with invalid timestamps
    df = df.dropna(
        subset=["measured_at"]
    )

    # Convert UTC → IST
    df["measured_at_ist"] = (
        df["measured_at"]
        .dt.tz_convert("Asia/Kolkata")
    )

    # --------------------------------------------------------
    # Time features
    # --------------------------------------------------------

    df["date"] = (
        df["measured_at_ist"]
        .dt.date
    )

    df["hour"] = (
        df["measured_at_ist"]
        .dt.hour
    )

    df["day_of_week"] = (
        df["measured_at_ist"]
        .dt.day_name()
    )

    df["day_of_week_num"] = (
        df["measured_at_ist"]
        .dt.dayofweek
    )

    # --------------------------------------------------------
    # Numeric values
    # --------------------------------------------------------

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    # Remove rows where essential values are missing
    df = df.dropna(
        subset=[
            "parameter",
            "value",
        ]
    )

    # --------------------------------------------------------
    # Remove physically impossible negative values
    # --------------------------------------------------------

    df = df[
        df["value"] >= 0
    ]

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    df = df.sort_values(
        "measured_at"
    ).reset_index(
        drop=True
    )

    return df


# ============================================================
# Unit normalization
# ============================================================

def normalize_units(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return df

    df = df.copy()

    df["value_standardized"] = pd.NA
    df["standardized_unit"] = pd.NA

    # --------------------------------------------------------
    # Normalize unit text
    # --------------------------------------------------------

    units = (
        df["unit"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.replace("µ", "u", regex=False)
        .str.replace("μ", "u", regex=False)
        .str.replace("³", "3", regex=False)
        .str.replace(" ", "", regex=False)
    )

    # --------------------------------------------------------
    # PM10 / PM2.5
    #
    # Standard unit:
    # µg/m³
    # --------------------------------------------------------

    pm_mask = df["parameter"].isin(
        ["pm10", "pm25"]
    )

    ug_mask = (
        pm_mask
        & units.str.contains(
            "ug/m3",
            na=False,
        )
    )

    mg_mask = (
        pm_mask
        & units.str.contains(
            "mg/m3",
            na=False,
        )
    )

    df.loc[
        ug_mask,
        "value_standardized",
    ] = df.loc[
        ug_mask,
        "value",
    ]

    df.loc[
        ug_mask,
        "standardized_unit",
    ] = "µg/m³"

    df.loc[
        mg_mask,
        "value_standardized",
    ] = (
        df.loc[
            mg_mask,
            "value",
        ] * 1000
    )

    df.loc[
        mg_mask,
        "standardized_unit",
    ] = "µg/m³"

    # --------------------------------------------------------
    # NO2 / SO2 / O3
    #
    # Standard unit:
    # µg/m³
    #
    # For ppb:
    #
    # µg/m³ = ppb × molecular_weight / 24.45
    # --------------------------------------------------------

    gas_parameters = [
        "no2",
        "so2",
        "o3",
    ]

    molecular_weights = {
        "no2": 46.0055,
        "so2": 64.066,
        "o3": 48.00,
    }

    for parameter in gas_parameters:

        parameter_mask = (
            df["parameter"] == parameter
        )

        ug_mask = (
            parameter_mask
            & units.str.contains(
                "ug/m3",
                na=False,
            )
        )

        mg_mask = (
            parameter_mask
            & units.str.contains(
                "mg/m3",
                na=False,
            )
        )

        ppb_mask = (
            parameter_mask
            & (units == "ppb")
        )

        df.loc[
            ug_mask,
            "value_standardized",
        ] = df.loc[
            ug_mask,
            "value",
        ]

        df.loc[
            ug_mask,
            "standardized_unit",
        ] = "µg/m³"

        df.loc[
            mg_mask,
            "value_standardized",
        ] = (
            df.loc[
                mg_mask,
                "value",
            ] * 1000
        )

        df.loc[
            mg_mask,
            "standardized_unit",
        ] = "µg/m³"

        df.loc[
            ppb_mask,
            "value_standardized",
        ] = (
            df.loc[
                ppb_mask,
                "value",
            ]
            * molecular_weights[parameter]
            / 24.45
        )

        df.loc[
            ppb_mask,
            "standardized_unit",
        ] = "µg/m³"

    # --------------------------------------------------------
    # CO
    #
    # Standard unit:
    # mg/m³
    # --------------------------------------------------------

    co_mask = (
        df["parameter"] == "co"
    )

    co_mg_mask = (
        co_mask
        & units.str.contains(
            "mg/m3",
            na=False,
        )
    )

    co_ug_mask = (
        co_mask
        & units.str.contains(
            "ug/m3",
            na=False,
        )
    )

    co_ppb_mask = (
        co_mask
        & (units == "ppb")
    )

    co_ppm_mask = (
        co_mask
        & (units == "ppm")
    )

    df.loc[
        co_mg_mask,
        "value_standardized",
    ] = df.loc[
        co_mg_mask,
        "value",
    ]

    df.loc[
        co_mg_mask,
        "standardized_unit",
    ] = "mg/m³"

    df.loc[
        co_ug_mask,
        "value_standardized",
    ] = (
        df.loc[
            co_ug_mask,
            "value",
        ] / 1000
    )

    df.loc[
        co_ug_mask,
        "standardized_unit",
    ] = "mg/m³"

    # Approximate conversion:
    # 1 ppm CO ≈ 1.145 mg/m³
    #
    # Therefore:
    # 1 ppb CO ≈ 0.001145 mg/m³

    df.loc[
        co_ppm_mask,
        "value_standardized",
    ] = (
        df.loc[
            co_ppm_mask,
            "value",
        ] * 1.145
    )

    df.loc[
        co_ppm_mask,
        "standardized_unit",
    ] = "mg/m³"

    df.loc[
        co_ppb_mask,
        "value_standardized",
    ] = (
        df.loc[
            co_ppb_mask,
            "value",
        ] * 0.001145
    )

    df.loc[
        co_ppb_mask,
        "standardized_unit",
    ] = "mg/m³"

    # --------------------------------------------------------
    # Convert standardized values to numeric
    # --------------------------------------------------------

    df["value_standardized"] = pd.to_numeric(
        df["value_standardized"],
        errors="coerce",
    )

    return df


# ============================================================
# Missing-data analysis
# ============================================================

def get_missing_data_analysis(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    expected_parameters = sorted(
        df["parameter"]
        .dropna()
        .unique()
    )

    results = []

    for parameter in expected_parameters:

        parameter_df = df[
            df["parameter"] == parameter
        ]

        total_rows = len(
            parameter_df
        )

        missing_values = int(
            parameter_df[
                "value_standardized"
            ].isna().sum()
        )

        valid_values = (
            total_rows
            - missing_values
        )

        missing_percentage = (
            missing_values
            / total_rows
            * 100
            if total_rows
            else 0
        )

        results.append(
            {
                "parameter": parameter,
                "total_rows": total_rows,
                "valid_values": valid_values,
                "missing_values": missing_values,
                "missing_percentage": round(
                    missing_percentage,
                    2,
                ),
            }
        )

    return pd.DataFrame(
        results
    )


# ============================================================
# Outlier detection using IQR
# ============================================================

def detect_outliers(
    df: pd.DataFrame,
    window: int = 24,
    robust_z_threshold: float = 3.5,
    minimum_deviation_percent: float = 20.0,
) -> pd.DataFrame:

    if df.empty:
        return df

    df = df.copy()

    # --------------------------------------------------------
    # Default columns
    # --------------------------------------------------------

    df["is_statistical_anomaly"] = False
    df["robust_z_score"] = pd.NA
    df["local_median"] = pd.NA
    df["deviation_percent"] = pd.NA

    # --------------------------------------------------------
    # Analyze each pollutant separately
    # --------------------------------------------------------

    for parameter in (
        df["parameter"]
        .dropna()
        .unique()
    ):

        mask = (
            df["parameter"] == parameter
        )

        parameter_df = (
            df.loc[
                mask,
                [
                    "measured_at",
                    "value_standardized",
                ],
            ]
            .sort_values("measured_at")
        )

        if len(parameter_df) < 5:
            continue

        values = parameter_df[
            "value_standardized"
        ]

        # ----------------------------------------------------
        # Rolling local median
        # ----------------------------------------------------

        local_median = (
            values
            .rolling(
                window=window,
                center=True,
                min_periods=5,
            )
            .median()
        )

        # ----------------------------------------------------
        # Absolute deviation from local median
        # ----------------------------------------------------

        absolute_deviation = (
            values - local_median
        ).abs()

        # ----------------------------------------------------
        # Rolling MAD
        # ----------------------------------------------------

        mad = (
            absolute_deviation
            .rolling(
                window=window,
                center=True,
                min_periods=5,
            )
            .median()
        )

        # ----------------------------------------------------
        # Percentage deviation from local median
        # ----------------------------------------------------

        deviation_percent = (
            absolute_deviation
            / local_median.abs().replace(
                0,
                pd.NA,
            )
        ) * 100

        # ----------------------------------------------------
        # Robust Z-score
        # ----------------------------------------------------

        robust_z = (
            0.6745
            * (
                values - local_median
            )
            / mad.replace(
                0,
                pd.NA,
            )
        )

        # ----------------------------------------------------
        # Store calculated values
        # ----------------------------------------------------

        df.loc[
            parameter_df.index,
            "local_median",
        ] = local_median

        df.loc[
            parameter_df.index,
            "deviation_percent",
        ] = deviation_percent

        df.loc[
            parameter_df.index,
            "robust_z_score",
        ] = robust_z

        # ----------------------------------------------------
        # Statistical anomaly
        #
        # BOTH conditions must be satisfied:
        #
        # 1. Robust Z-score is high
        # 2. Actual deviation is meaningful
        #
        # This prevents tiny sensor variations from being
        # classified as anomalies.
        # ----------------------------------------------------

        anomaly_mask = (
            robust_z.abs()
            > robust_z_threshold
        ) & (
            deviation_percent
            >= minimum_deviation_percent
        )

        anomaly_mask = anomaly_mask.fillna(
            False
        )

        df.loc[
            parameter_df.index,
            "is_statistical_anomaly",
        ] = anomaly_mask

    return df
# ============================================================
# Complete processing pipeline
# ============================================================

def process_city_data(
    df: pd.DataFrame
) -> pd.DataFrame:

    if df.empty:
        return df

    df = prepare_data(df)

    df = normalize_units(df)

    df = detect_outliers(df)

    return df


# ============================================================
# Data-quality summary
# ============================================================

def get_data_quality(
    df: pd.DataFrame,
) -> dict:

    if df.empty:
        return {
            "total_rows": 0,
            "missing_values": 0,
            "duplicate_rows": 0,
            "outliers": 0,
            "parameters": [],
        }

    return {
        "total_rows": len(df),

        "missing_values": int(
            df["value_standardized"]
            .isna()
            .sum()
        ),

        "duplicate_rows": int(
            df.duplicated(
                subset=[
                    "measured_at",
                    "parameter",
                    "value",
                ]
            ).sum()
        ),

        "statistical_anomalies": int(
            df["is_statistical_anomaly"].sum()
        ),

        "parameters": sorted(
            df["parameter"]
            .dropna()
            .unique()
            .tolist()
        ),
    }


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    import sqlite3

    DB_PATH = (
        PROJECT_DIR
        / "db"
        / "aqi.db"
    )

    conn = sqlite3.connect(DB_PATH)

    city = "Mumbai"

    print("=" * 60)
    print("CityAir — Pandas Data Processing")
    print("=" * 60)

    # Load raw data for testing
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

    raw_df = pd.DataFrame(
        raw_readings,
        columns=[
            "measured_at",
            "parameter",
            "value",
            "unit",
        ],
    )

    # Process with Pandas
    df = process_city_data(raw_df)

    print(
        f"\nProcessed rows: {len(df)}"
    )

    # Show sample
    print("\nProcessed Sample:")

    columns = [
        "measured_at_ist",
        "parameter",
        "value",
        "unit",
        "value_standardized",
        "standardized_unit",
        "date",
        "hour",
        "day_of_week",
        "is_statistical_anomaly",
        "robust_z_score",
    ]

    print(
        df[columns]
        .head(15)
        .to_string(index=False)
    )

    # Data quality
    print("\nData Quality:")

    quality = get_data_quality(df)

    for key, value in quality.items():
        print(f"{key}: {value}")

    # Missing-data analysis
    print("\nMissing Data Analysis:")
    print("-" * 60)

    missing = get_missing_data_analysis(df)

    if not missing.empty:
        print(
            missing.to_string(index=False)
        )

    # Statistical anomaly summary
    print("\nStatistical Anomaly Analysis:")
    print("-" * 60)

    anomaly_summary = (
        df.groupby("parameter")
        .agg(
            observations=("value_standardized", "count"),
            statistical_anomalies=(
                "is_statistical_anomaly",
                "sum",
            ),
        )
        .reset_index()
    )

    print(
        anomaly_summary.to_string(index=False)
    )

    # Sample anomalies
    print("\nSample Statistical Anomalies:")
    print("-" * 60)

    anomalies = df[
        df["is_statistical_anomaly"]
    ]

    if anomalies.empty:
        print(
            "No statistical anomalies detected."
        )
    else:
        print(
            anomalies[
                [
                    "measured_at_ist",
                    "parameter",
                    "value",
                    "unit",
                    "value_standardized",
                    "standardized_unit",
                    "robust_z_score",
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

    conn.close()