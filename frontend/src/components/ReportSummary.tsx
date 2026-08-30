import { CityReport } from "../api/aeroiq";
import { AQIStatus } from "./AQIStatus";

export function ReportSummary({ report }: { report: CityReport }) {
  const { city, analytics, data_summary } = report;
  const aqi = analytics.aqi;

  return (
    <section className="border-b border-mist/70">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Summary</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          City at a glance
        </h2>

        <dl className="mt-8 grid grid-cols-2 gap-6 sm:grid-cols-5">
          <div>
            <dt className="text-xs uppercase tracking-wider text-haze">City</dt>
            <dd className="mt-1 font-medium text-graphite">{city}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-haze">AQI</dt>
            <dd className="mt-1 font-mono font-tabular text-graphite">
              {aqi?.aqi != null ? Math.round(aqi.aqi) : "—"}
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-haze">Category</dt>
            <dd className="mt-1">
              <AQIStatus category={aqi?.category} />
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-haze">
              Dominant pollutant
            </dt>
            <dd className="mt-1 font-medium text-graphite">
              {aqi?.dominant_pollutant_label ?? "—"}
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-haze">
              Observations analyzed
            </dt>
            <dd className="mt-1 font-mono font-tabular text-graphite">
              {data_summary.processed_rows.toLocaleString()}
            </dd>
          </div>
        </dl>

        <p className="mt-10 max-w-2xl text-[15px] leading-relaxed text-haze">
          Based on {data_summary.processed_rows.toLocaleString()} processed
          observations, {city}'s air quality currently sits in the{" "}
          <span className="font-medium text-graphite">
            {aqi?.category?.toLowerCase() ?? "unreported"}
          </span>{" "}
          category
          {aqi?.dominant_pollutant_label &&
            `, driven primarily by ${aqi.dominant_pollutant_label}`}
          .
        </p>
      </div>
    </section>
  );
}
