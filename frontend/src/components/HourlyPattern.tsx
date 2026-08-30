import { useMemo, useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";
import { Extremes, HourlyPatternPoint } from "../api/aeroiq";
import { ContourMotif } from "./ContourMotif";
import { formatValue, parameterLabel } from "../lib/aqi";

interface HourlyPatternProps {
  hourlyPatterns: HourlyPatternPoint[];
  hourlyExtremes: Extremes | null;
}

export function HourlyPattern({ hourlyPatterns, hourlyExtremes }: HourlyPatternProps) {
  const availableParams = useMemo(
    () => Array.from(new Set(hourlyPatterns.map((p) => p.parameter))),
    [hourlyPatterns],
  );

  const [parameter, setParameter] = useState(
    availableParams.includes("pm25") ? "pm25" : availableParams[0],
  );

  const data = useMemo(
    () =>
      hourlyPatterns
        .filter((p) => p.parameter === parameter)
        .sort((a, b) => Number(a.hour_ist) - Number(b.hour_ist)),
    [hourlyPatterns, parameter],
  );

  if (!data.length) {
    return (
      <p className="text-sm italic text-haze">
        No hourly pattern data is available for this city.
      </p>
    );
  }

  const highestHour = hourlyExtremes?.highest_hour_ist;
  const lowestHour = hourlyExtremes?.lowest_hour_ist;

  return (
    <section className="relative overflow-hidden border-b border-mist/70">
      <ContourMotif
        className="pointer-events-none absolute inset-0 h-full w-full text-instrument"
        opacity={0.06}
      />

      <div className="relative mx-auto max-w-6xl px-6 py-16">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-widest text-haze">Timing</p>
            <h2 className="mt-2 font-display text-2xl text-graphite">
              When is pollution highest?
            </h2>
          </div>

          {availableParams.length > 1 && (
            <div className="flex gap-2">
              {availableParams.map((p) => (
                <button
                  key={p}
                  onClick={() => setParameter(p)}
                  className={`px-3 py-1 text-xs uppercase tracking-wider transition-colors ${
                    p === parameter
                      ? "bg-instrument text-overcast"
                      : "border border-mist text-haze hover:border-haze"
                  }`}
                >
                  {parameterLabel(p)}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="mt-10 h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
              <CartesianGrid stroke="#E4E6E2" vertical={false} />
              <XAxis
                dataKey="hour_ist"
                tick={{ fill: "#6B7178", fontSize: 11 }}
                axisLine={{ stroke: "#E4E6E2" }}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "#6B7178", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={40}
              />
              <Tooltip
                contentStyle={{
                  background: "#F5F6F4",
                  border: "1px solid #E4E6E2",
                  borderRadius: 0,
                  fontSize: 13,
                }}
              />
              <Bar dataKey="average" radius={[2, 2, 0, 0]}>
                {data.map((entry) => {
                  const isHigh = entry.hour_ist === highestHour;
                  const isLow = entry.hour_ist === lowestHour;
                  return (
                    <Cell
                      key={entry.hour_ist}
                      fill={
                        isHigh ? "#C5502F" : isLow ? "#2E9E5B" : "#B7BEC0"
                      }
                    />
                  );
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {hourlyExtremes && (
          <div className="mt-6 flex flex-wrap gap-8 text-sm">
            <p className="text-haze">
              Highest around{" "}
              <span className="font-mono font-tabular text-graphite">
                {hourlyExtremes.highest_hour_ist} IST
              </span>{" "}
              at {formatValue(hourlyExtremes.highest_average)} µg/m³
            </p>
            <p className="text-haze">
              Lowest around{" "}
              <span className="font-mono font-tabular text-graphite">
                {hourlyExtremes.lowest_hour_ist} IST
              </span>{" "}
              at {formatValue(hourlyExtremes.lowest_average)} µg/m³
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
