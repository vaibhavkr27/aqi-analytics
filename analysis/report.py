from __future__ import annotations

from typing import Any

from .data_loader import get_city_data
from .processor import process_city_data
from .analytics import get_city_analytics
from .insights import generate_insights


def generate_city_report(
    city_name: str,
) -> dict[str, Any]:
    """
    Generate the complete AQI analysis report
    for a user-entered city.
    """

    city_name = city_name.strip()

    if not city_name:
        return {
            "city": city_name,
            "error": "City name cannot be empty.",
        }

    # --------------------------------------------------------
    # 1. Load raw city data
    # --------------------------------------------------------

    raw_df = get_city_data(
        city_name
    )

    if raw_df.empty:
        return {
            "city": city_name,
            "error": (
                f"No AQI data found for "
                f"{city_name}."
            ),
        }

    # --------------------------------------------------------
    # 2. Process raw data
    # --------------------------------------------------------

    processed_df = process_city_data(
        raw_df
    )

    if processed_df.empty:
        return {
            "city": city_name,
            "error": (
                "Data was found, but "
                "processing produced no records."
            ),
        }

    # --------------------------------------------------------
    # 3. Generate analytics
    # --------------------------------------------------------

    analytics_report = get_city_analytics(
        processed_df,
        city_name,
    )

    # --------------------------------------------------------
    # 4. Generate human-readable insights
    # --------------------------------------------------------

    insight_report = generate_insights(
        analytics_report
    )

    # --------------------------------------------------------
    # 5. Final report
    # --------------------------------------------------------

    return {
        "city": city_name,

        "data_summary": {
            "raw_rows": len(raw_df),
            "processed_rows": len(processed_df),
        },

        "analytics": analytics_report,

        "insights": insight_report,
    }


# ============================================================
# Standalone Test / Final Report
# ============================================================

def print_city_report(
    report: dict[str, Any],
) -> None:
    """
    Print a clean, user-facing AQI report.
    """

    if "error" in report:

        print()
        print("=" * 70)
        print("CityAir — AQI Analysis")
        print("=" * 70)

        print(
            f"\nError: {report['error']}"
        )

        return

    city = report["city"]

    analytics = report.get(
        "analytics",
        {},
    )

    insights = report.get(
        "insights",
        {},
    )

    data_summary = report.get(
        "data_summary",
        {},
    )

    # ========================================================
    # Header
    # ========================================================

    print()
    print("=" * 70)
    print("CityAir — Air Quality Analysis")
    print("=" * 70)

    print(
        f"\nCity: {city}"
    )

    print(
        f"Raw observations: "
        f"{data_summary.get('raw_rows', 0)}"
    )

    print(
        f"Processed observations: "
        f"{data_summary.get('processed_rows', 0)}"
    )

    # ========================================================
    # AQI
    # ========================================================

    print()
    print("-" * 70)
    print("AQI")
    print("-" * 70)

    aqi = analytics.get(
        "aqi",
        {},
    )

    if aqi.get("status") == "valid":

        print(
            f"AQI: {aqi.get('aqi')}"
        )

        print(
            f"Category: {aqi.get('category')}"
        )

        dominant = aqi.get(
            "dominant_pollutant_label"
        )

        if dominant:

            print(
                f"Dominant pollutant: "
                f"{dominant}"
            )

        print(
            "\nPollutant Sub-Indices:"
        )

        for item in aqi.get(
            "subindices",
            [],
        ):

            label = item.get(
                "label",
                item.get(
                    "parameter",
                    "Unknown",
                ),
            )

            if item.get("status") == "valid":

                print(
                    f"  {label}: "
                    f"{item.get('sub_index')} "
                    f"({item.get('category')})"
                )

            else:

                reason = item.get(
                    "reason",
                    "Insufficient data",
                )

                print(
                    f"  {label}: "
                    f"Insufficient data"
                )

                print(
                    f"    {reason}"
                )

    elif aqi.get("status") == "insufficient_data":

        print(
            "AQI: Not available"
        )

        print(
            f"Reason: "
            f"{aqi.get('reason', 'Insufficient data')}"
        )

    else:

        print(
            "AQI: Not available"
        )

    # ========================================================
    # Pollutant Summary
    # ========================================================

    print()
    print("-" * 70)
    print("30-DAY POLLUTANT SUMMARY")
    print("-" * 70)

    statistics = analytics.get(
        "pollutant_statistics",
        [],
    )

    if not statistics:

        print(
            "No pollutant statistics available."
        )

    else:

        for item in statistics:

            parameter = item.get(
                "parameter",
                "unknown",
            )

            average = item.get(
                "average"
            )

            median = item.get(
                "median"
            )

            minimum = item.get(
                "minimum"
            )

            maximum = item.get(
                "maximum"
            )

            p95 = item.get(
                "p95"
            )

            p99 = item.get(
                "p99"
            )

            print()
            print(
                parameter.upper()
            )

            print(
                f"  Average : {average}"
            )

            print(
                f"  Median  : {median}"
            )

            print(
                f"  Minimum : {minimum}"
            )

            print(
                f"  Maximum : {maximum}"
            )

            print(
                f"  P95     : {p95}"
            )

            print(
                f"  P99     : {p99}"
            )

    # ========================================================
    # Key Insights
    # ========================================================

    print()
    print("-" * 70)
    print("KEY INSIGHTS")
    print("-" * 70)

    insight_sections = [
        (
            "POLLUTION SPIKES",
            "pollution_spikes",
        ),
        (
            "TOP POLLUTION PEAKS",
            "peak_concentrations",
        ),
        (
            "HOURLY PATTERNS",
            "hourly_patterns",
        ),
        (
            "DAILY PATTERNS",
            "daily_patterns",
        ),
    ]

    any_insights = False

    for title, key in insight_sections:

        section = insights.get(
            key,
            [],
        )

        if not section:
            continue

        any_insights = True

        print()
        print(title)

        for insight in section:

            print(
                f"  • {insight}"
            )

    if not any_insights:

        print(
            "No notable insights were generated."
        )

    # ========================================================
    # Weekday / Weekend
    # ========================================================

    print()
    print("-" * 70)
    print("WEEKDAY VS WEEKEND")
    print("-" * 70)

    weekday_weekend = analytics.get(
        "weekday_weekend",
        [],
    )

    if not weekday_weekend:

        print(
            "No weekday/weekend comparison available."
        )

    else:

        for item in weekday_weekend:

            day_type = item.get(
                "day_type",
                "unknown",
            )

            parameter = item.get(
                "parameter",
                "unknown",
            )

            average = item.get(
                "average"
            )

            print(
                f"{day_type.title():<10} "
                f"{parameter.upper():<6} "
                f"average: {average}"
            )

    # ========================================================
    # Data Quality
    # ========================================================

    print()
    print("-" * 70)
    print("DATA QUALITY")
    print("-" * 70)

    print(
        f"Rows analyzed: "
        f"{data_summary.get('processed_rows', 0)}"
    )

    coverage = analytics.get(
        "data_coverage",
        [],
    )

    if coverage:

        for item in coverage:

            parameter = item.get(
                "parameter",
                "unknown",
            )

            observations = item.get(
                "observations",
                0,
            )

            days = item.get(
                "days_available",
                0,
            )

            print(
                f"{parameter.upper():<6} "
                f"{observations} observations, "
                f"{days} days available"
            )

    else:

        print(
            "Coverage information unavailable."
        )

    # ========================================================
    # Final Summary
    # ========================================================

    print()
    print("=" * 70)

    if aqi.get("status") == "valid":

        print(
            f"{city}: AQI "
            f"{aqi.get('aqi')} "
            f"({aqi.get('category')})"
        )

        dominant = aqi.get(
            "dominant_pollutant_label"
        )

        if dominant:

            print(
                f"Dominant pollutant: "
                f"{dominant}"
            )

    else:

        print(
            f"{city}: AQI unavailable"
        )

    print("=" * 70)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("CityAir — AQI Analysis")
    print("=" * 70)

    city = input(
        "\nEnter city name: "
    ).strip()

    report = generate_city_report(
        city
    )

    print_city_report(
        report
    )