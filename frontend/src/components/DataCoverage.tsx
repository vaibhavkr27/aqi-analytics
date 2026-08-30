import { DataCoverageRow } from "../api/aeroiq";
import { parameterLabel } from "../lib/aqi";

export function DataCoverage({ rows }: { rows: DataCoverageRow[] }) {
  if (!rows.length) return null;

  return (
    <section id="coverage" className="border-b border-mist/70">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Transparency</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          How much data was available?
        </h2>

        <div className="mt-8 overflow-x-auto">
          <table className="w-full min-w-[640px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-mist text-left text-xs uppercase tracking-wider text-haze">
                <th className="py-3 pr-4 font-normal">Pollutant</th>
                <th className="py-3 pr-4 font-normal">Observations</th>
                <th className="py-3 pr-4 font-normal">Days available</th>
                <th className="py-3 pr-4 font-normal">Hours available</th>
                <th className="py-3 pr-4 font-normal">First reading</th>
                <th className="py-3 pr-4 font-normal">Last reading</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.parameter} className="border-b border-mist/60">
                  <td className="py-3 pr-4 font-medium text-graphite">
                    {parameterLabel(row.parameter)}
                  </td>
                  <td className="py-3 pr-4 font-mono font-tabular text-graphite">
                    {row.observations.toLocaleString()}
                  </td>
                  <td className="py-3 pr-4 font-mono font-tabular text-graphite">
                    {row.days_available}
                  </td>
                  <td className="py-3 pr-4 font-mono font-tabular text-graphite">
                    {row.hours_available}
                  </td>
                  <td className="py-3 pr-4 text-haze">{row.first_reading}</td>
                  <td className="py-3 pr-4 text-haze">{row.last_reading}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
