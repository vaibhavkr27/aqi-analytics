import { useMemo } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { WeekdayWeekendPoint } from "../api/aeroiq";
import { parameterLabel } from "../lib/aqi";

interface WeekdayWeekendProps {
  data: WeekdayWeekendPoint[];
}

export function WeekdayWeekend({ data }: WeekdayWeekendProps) {
  const chartData = useMemo(() => {
    const parameters = Array.from(new Set(data.map((d) => d.parameter)));
    return parameters.map((param) => {
      const weekday = data.find((d) => d.parameter === param && d.day_type === "weekday");
      const weekend = data.find((d) => d.parameter === param && d.day_type === "weekend");
      return {
        parameter: parameterLabel(param),
        Weekday: weekday?.average ?? null,
        Weekend: weekend?.average ?? null,
      };
    });
  }, [data]);

  if (!chartData.length) return null;

  return (
    <section className="border-b border-mist/70">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Rhythm</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          Weekday vs weekend
        </h2>

        <div className="mt-10 h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 16, left: -16, bottom: 0 }}>
              <CartesianGrid stroke="#E4E6E2" vertical={false} />
              <XAxis
                dataKey="parameter"
                tick={{ fill: "#6B7178", fontSize: 12 }}
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
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="Weekday" fill="#2C4A6E" radius={[2, 2, 0, 0]} />
              <Bar dataKey="Weekend" fill="#B7BEC0" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
