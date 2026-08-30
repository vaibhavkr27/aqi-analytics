import { Analytics, CityReport } from "../api/aeroiq";

interface QuickStatsProps {
  report: CityReport;
}

function availablePollutantCount(analytics: Analytics): { available: number; total: number } {
  const total = analytics.pollutant_statistics.length;
  const available = analytics.pollutant_statistics.filter(
    (p) => p.aqi_subindex !== null && p.aqi_subindex !== undefined,
  ).length;
  return { available: available || total, total: total || 6 };
}

function analysisPeriod(analytics: Analytics): string {
  const trends = analytics.daily_trends;
  if (!trends.length) return "—";
  const days = trends.map((t) => t.day).sort();
  return `${days[0]} → ${days[days.length - 1]}`;
}

export function QuickStats({ report }: QuickStatsProps) {
  const { analytics, data_summary } = report;
  const { available, total } = availablePollutantCount(analytics);

  const stats = [
    {
      label: "Observations",
      value: data_summary.processed_rows.toLocaleString(),
    },
    {
      label: "Pollutants",
      value: `${available} / ${total}`,
    },
    {
      label: "Dominant pollutant",
      value: analytics.aqi?.dominant_pollutant_label ?? "—",
    },
    {
      label: "Analysis period",
      value: analysisPeriod(analytics),
    },
  ];

  return (
    <section className="border-b border-mist/70">
      <div className="mx-auto grid max-w-6xl grid-cols-2 gap-8 px-6 py-8 sm:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label}>
            <p className="text-xs uppercase tracking-widest text-haze">{stat.label}</p>
            <p className="mt-1 font-mono font-tabular text-lg text-graphite">
              {stat.value}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
