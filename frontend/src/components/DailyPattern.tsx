import { DailyTrendPoint, Extremes } from "../api/aeroiq";
import { TrendChart } from "./TrendChart";
import { formatDateShort, formatValue } from "../lib/aqi";

interface DailyPatternProps {
  dailyExtremes: Extremes | null;
  dailyTrends: DailyTrendPoint[];
}

export function DailyPattern({ dailyExtremes, dailyTrends }: DailyPatternProps) {
  return (
    <section className="border-b border-mist/70">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Daily rhythm</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          Best and worst days
        </h2>

        {dailyExtremes && (
          <div className="mt-8 grid grid-cols-1 gap-px bg-mist sm:grid-cols-2">
            <div className="bg-overcast p-6">
              <p className="text-xs uppercase tracking-wider text-haze">
                Highest daily average
              </p>
              <p className="mt-2 font-mono font-tabular text-3xl text-aqi-poor">
                {formatValue(dailyExtremes.highest_average)}
                <span className="ml-1 text-sm text-haze">µg/m³</span>
              </p>
              <p className="mt-1 text-sm text-haze">
                {formatDateShort(dailyExtremes.highest_day)}
              </p>
            </div>
            <div className="bg-overcast p-6">
              <p className="text-xs uppercase tracking-wider text-haze">
                Lowest daily average
              </p>
              <p className="mt-2 font-mono font-tabular text-3xl text-aqi-good">
                {formatValue(dailyExtremes.lowest_average)}
                <span className="ml-1 text-sm text-haze">µg/m³</span>
              </p>
              <p className="mt-1 text-sm text-haze">
                {formatDateShort(dailyExtremes.lowest_day)}
              </p>
            </div>
          </div>
        )}

        <div className="mt-10">
          <TrendChart dailyTrends={dailyTrends} />
        </div>
      </div>
    </section>
  );
}
