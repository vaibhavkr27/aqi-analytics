import { useMemo } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { DailyTrendPoint } from "../api/aeroiq";
import { formatDateShort } from "../lib/aqi";

interface TrendChartProps {
  dailyTrends: DailyTrendPoint[];
}

function pivotByDay(
  trends: DailyTrendPoint[],
  parameters: string[],
): Array<Record<string, number | string>> {
  const byDay = new Map<string, Record<string, number | string>>();

  for (const point of trends) {
    if (!parameters.includes(point.parameter)) continue;
    const row = byDay.get(point.day) ?? { day: point.day };
    row[point.parameter] = point.average;
    byDay.set(point.day, row);
  }

  return Array.from(byDay.values()).sort((a, b) =>
    String(a.day).localeCompare(String(b.day)),
  );
}

export function TrendChart({ dailyTrends }: TrendChartProps) {
  const data = useMemo(() => pivotByDay(dailyTrends, ["pm25", "pm10"]), [dailyTrends]);

  if (!data.length) {
    return (
      <p className="text-sm italic text-haze">
        No daily trend data is available for this city.
      </p>
    );
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
          <CartesianGrid stroke="#E4E6E2" vertical={false} />
          <XAxis
            dataKey="day"
            tickFormatter={(d: string) => formatDateShort(d)}
            tick={{ fill: "#6B7178", fontSize: 12 }}
            axisLine={{ stroke: "#E4E6E2" }}
            tickLine={false}
            minTickGap={24}
          />
          <YAxis
            tick={{ fill: "#6B7178", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={40}
          />
          <Tooltip
            labelFormatter={(d) => formatDateShort(String(d))}
            contentStyle={{
              background: "#F5F6F4",
              border: "1px solid #E4E6E2",
              borderRadius: 0,
              fontSize: 13,
            }}
          />
          <Line
            type="monotone"
            dataKey="pm25"
            name="PM2.5"
            stroke="#2C4A6E"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="pm10"
            name="PM10"
            stroke="#6B7178"
            strokeWidth={1.5}
            strokeDasharray="4 3"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
