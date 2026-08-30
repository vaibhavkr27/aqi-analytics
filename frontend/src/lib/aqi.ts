export const PARAMETER_LABELS: Record<string, string> = {
  pm25: "PM2.5",
  pm10: "PM10",
  no2: "NO₂",
  so2: "SO₂",
  co: "CO",
  o3: "O₃",
};

export function parameterLabel(parameter: string): string {
  return PARAMETER_LABELS[parameter] ?? parameter.toUpperCase();
}

/**
 * Maps an AQI category string (case-insensitive) to the fixed,
 * functional AQI color tokens defined in tailwind.config.js.
 * This is the ONLY place saturated color is chosen from data.
 */
export function categoryColorClass(category: string | null | undefined): {
  text: string;
  bg: string;
  border: string;
} {
  const key = (category ?? "").trim().toLowerCase();

  switch (key) {
    case "good":
      return {
        text: "text-aqi-good",
        bg: "bg-aqi-good/10",
        border: "border-aqi-good/30",
      };
    case "satisfactory":
      return {
        text: "text-aqi-satisfactory",
        bg: "bg-aqi-satisfactory/10",
        border: "border-aqi-satisfactory/30",
      };
    case "moderate":
      return {
        text: "text-aqi-moderate",
        bg: "bg-aqi-moderate/10",
        border: "border-aqi-moderate/30",
      };
    case "poor":
      return {
        text: "text-aqi-poor",
        bg: "bg-aqi-poor/10",
        border: "border-aqi-poor/30",
      };
    case "very poor":
    case "verypoor":
      return {
        text: "text-aqi-verypoor",
        bg: "bg-aqi-verypoor/10",
        border: "border-aqi-verypoor/30",
      };
    case "severe":
      return {
        text: "text-aqi-severe",
        bg: "bg-aqi-severe/10",
        border: "border-aqi-severe/30",
      };
    default:
      return {
        text: "text-haze",
        bg: "bg-mist/40",
        border: "border-mist",
      };
  }
}

export function formatValue(
  value: number | null | undefined,
  digits?: number,
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "—";
  }

  if (digits !== undefined) {
    return value.toFixed(digits);
  }

  const abs = Math.abs(value);

  if (abs >= 100) return value.toFixed(0);
  if (abs >= 10) return value.toFixed(1);
  // Preserve meaningful precision for small values (e.g. CO ~0.3-0.5)
  // instead of collapsing them to "0.0".
  return value.toFixed(2);
}

export function formatDeviation(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "—";
  }
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(0)}%`;
}

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

/**
 * Formats an ISO-ish timestamp string (e.g. "2026-08-05 17:00:00+05:30")
 * into "August 5, 2026 · 17:00 IST". Falls back to the raw string if
 * the shape doesn't match, rather than throwing.
 */
export function formatDateTime(timestamp: string | null | undefined): string {
  if (!timestamp) return "Unknown time";

  try {
    const [datePart, timePartRaw] = timestamp.trim().split(/[ T]/);
    const [year, month, day] = datePart.split("-");
    const hour = (timePartRaw ?? "00:00").slice(0, 5);
    const monthName = MONTHS[Number(month) - 1] ?? month;

    return `${monthName} ${Number(day)}, ${year} · ${hour} IST`;
  } catch {
    return timestamp;
  }
}

export function formatDateShort(day: string | null | undefined): string {
  if (!day) return "—";
  try {
    const [year, month, dayNum] = day.split("-");
    const monthName = MONTHS[Number(month) - 1]?.slice(0, 3) ?? month;
    return `${monthName} ${Number(dayNum)}`;
  } catch {
    return day;
  }
}
