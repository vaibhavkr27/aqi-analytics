import { DailyTrendPoint } from "../api/aeroiq";
import { TrendChart } from "./TrendChart";

export function TrendSection({ dailyTrends }: { dailyTrends: DailyTrendPoint[] }) {
  return (
    <section id="trends" className="border-b border-mist/70">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Trends</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          How pollution changes over time
        </h2>
        <p className="mt-2 max-w-xl text-sm text-haze">
          PM2.5 daily average, with PM10 shown for comparison.
        </p>

        <div className="mt-10">
          <TrendChart dailyTrends={dailyTrends} />
        </div>
      </div>
    </section>
  );
}
