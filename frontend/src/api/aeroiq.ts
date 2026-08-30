/**
 * AeroIQ API layer.
 *
 * This is the ONLY file in the app allowed to talk to the network.
 * Every component receives data as props from whatever called
 * getCityReport() — never fetch() directly inside a component.
 */

const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://127.0.0.1:8000";

// ------------------------------------------------------------------
// Types — mirrors the backend's response shape.
// Every nested field is optional/nullable because pollutant
// availability varies by city and time window. Never assume a
// fixed set of pollutants is present.
// ------------------------------------------------------------------

export interface AqiSubindex {
  parameter: string;
  label: string;
  status: "valid" | "insufficient_data";
  concentration?: number;
  unit?: string;
  sub_index?: number;
  category?: string;
  averaging_hours: number;
  observations: number;
  timestamp: string;
  reason?: string;
}

export interface AqiSummary {
  status: "valid" | "insufficient_data" | "no_data";
  aqi: number | null;
  category: string | null;
  dominant_pollutant: string | null;
  dominant_pollutant_label: string | null;
  subindices: AqiSubindex[];
}

export interface PollutantStat {
  parameter: string;
  observations: number;
  average: number;
  median: number;
  minimum: number;
  maximum: number;
  standard_deviation?: number;
  p95?: number;
  p99?: number;
  unit?: string;
  aqi_subindex?: number | null;
  aqi_category?: string | null;
  averaging_window?: string;
}

export interface DailyTrendPoint {
  day: string;
  parameter: string;
  average: number;
  minimum: number;
  maximum: number;
  observations: number;
}

export interface HourlyPatternPoint {
  hour_ist: string;
  parameter: string;
  average: number;
  minimum: number;
  maximum: number;
  observations: number;
}

export interface WeekdayWeekendPoint {
  day_type: "weekday" | "weekend" | string;
  parameter: string;
  average: number;
  minimum: number;
  maximum: number;
  observations: number;
}

export interface DayOfWeekPoint {
  day_of_week: string;
  parameter: string;
  average: number;
}

export type Correlations = Record<string, Record<string, number>>;

export interface PollutionPeak {
  timestamp: string;
  parameter: string;
  value: number;
  unit?: string;
}

export interface Anomaly {
  timestamp: string;
  parameter: string;
  value: number;
  unit?: string;
  local_median: number | null;
  deviation_percent: number | null;
  robust_z_score?: number | null;
}

export interface DataCoverageRow {
  parameter: string;
  observations: number;
  days_available: number;
  hours_available: number;
  first_reading: string;
  last_reading: string;
}

export interface Extremes {
  parameter: string;
  highest_day?: string;
  highest_hour_ist?: string;
  highest_average: number;
  lowest_day?: string;
  lowest_hour_ist?: string;
  lowest_average: number;
}

export interface Analytics {
  aqi?: AqiSummary;
  pollutant_statistics: PollutantStat[];
  daily_trends: DailyTrendPoint[];
  hourly_patterns: HourlyPatternPoint[];
  weekday_weekend: WeekdayWeekendPoint[];
  day_of_week: DayOfWeekPoint[];
  correlations: Correlations;
  pollution_peaks: PollutionPeak[];
  anomalies: Anomaly[];
  data_coverage: DataCoverageRow[];
  daily_extremes: Extremes | null;
  hourly_extremes: Extremes | null;
}

export interface Insights {
  pollution_spikes: string[];
  peak_concentrations: string[];
  hourly_patterns: string[];
  daily_patterns: string[];
}

export interface CityReport {
  city: string;
  data_summary: {
    raw_rows: number;
    processed_rows: number;
  };
  analytics: Analytics;
  insights: Insights;
}

// ------------------------------------------------------------------
// Errors
// ------------------------------------------------------------------

export type AeroIQErrorKind =
  | "empty_query"
  | "not_found"
  | "unavailable"
  | "malformed"
  | "network";

export class AeroIQError extends Error {
  kind: AeroIQErrorKind;

  constructor(kind: AeroIQErrorKind, message: string) {
    super(message);
    this.kind = kind;
    this.name = "AeroIQError";
  }
}

// ------------------------------------------------------------------
// getCityReport
// ------------------------------------------------------------------

export async function getCityReport(city: string): Promise<CityReport> {
  const trimmed = city.trim();

  if (!trimmed) {
    throw new AeroIQError("empty_query", "City name cannot be empty.");
  }

  const url = `${API_BASE_URL}/api/report?city=${encodeURIComponent(trimmed)}`;

  let response: Response;

  try {
    response = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
    });
  } catch {
    // Network failure, connection refused, CORS block, etc.
    throw new AeroIQError(
      "network",
      "The AeroIQ analysis service is currently unavailable.",
    );
  }

  if (response.status === 404) {
    throw new AeroIQError(
      "not_found",
      `No air-quality data was found for "${trimmed}".`,
    );
  }

  if (!response.ok) {
    throw new AeroIQError(
      "unavailable",
      "The AeroIQ analysis service is currently unavailable.",
    );
  }

  let data: unknown;

  try {
    data = await response.json();
  } catch {
    throw new AeroIQError(
      "malformed",
      "The AeroIQ analysis service returned an unexpected response.",
    );
  }

  if (
    typeof data !== "object" ||
    data === null ||
    !("analytics" in data) ||
    !("insights" in data)
  ) {
    throw new AeroIQError(
      "malformed",
      "The AeroIQ analysis service returned an unexpected response.",
    );
  }

  return data as CityReport;
}
