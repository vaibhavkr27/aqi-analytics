import { useState } from "react";
import { PollutantStat } from "../api/aeroiq";
import { formatValue, parameterLabel } from "../lib/aqi";

interface PollutantSummaryProps {
  pollutants: PollutantStat[];
}

const COLUMNS: { key: keyof PollutantStat; label: string }[] = [
  { key: "average", label: "Average" },
  { key: "median", label: "Median" },
  { key: "minimum", label: "Minimum" },
  { key: "maximum", label: "Maximum" },
  { key: "p95", label: "P95" },
  { key: "p99", label: "P99" },
];

export function PollutantSummary({ pollutants }: PollutantSummaryProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (!pollutants.length) return null;

  return (
    <section className="border-b border-mist/70">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Profile</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          30-Day Pollution Profile
        </h2>

        {/* Desktop / tablet table */}
        <div className="mt-8 hidden overflow-x-auto sm:block">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-mist text-left text-xs uppercase tracking-wider text-haze">
                <th className="py-3 pr-4 font-normal">Pollutant</th>
                {COLUMNS.map((col) => (
                  <th key={col.key} className="py-3 pr-4 font-normal">
                    {col.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pollutants.map((p) => (
                <tr key={p.parameter} className="border-b border-mist/60">
                  <td className="py-3 pr-4 font-medium text-graphite">
                    {parameterLabel(p.parameter)}
                  </td>
                  {COLUMNS.map((col) => (
                    <td
                      key={col.key}
                      className="py-3 pr-4 font-mono font-tabular text-graphite"
                    >
                      {formatValue(p[col.key] as number | undefined)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile: expandable per-pollutant summaries */}
        <div className="mt-8 space-y-2 sm:hidden">
          {pollutants.map((p) => {
            const isOpen = expanded === p.parameter;
            return (
              <div key={p.parameter} className="border border-mist">
                <button
                  className="flex w-full items-center justify-between px-4 py-3 text-left"
                  onClick={() => setExpanded(isOpen ? null : p.parameter)}
                  aria-expanded={isOpen}
                >
                  <span className="font-medium text-graphite">
                    {parameterLabel(p.parameter)}
                  </span>
                  <span className="font-mono font-tabular text-haze">
                    {formatValue(p.average)}
                  </span>
                </button>
                {isOpen && (
                  <div className="grid grid-cols-2 gap-3 border-t border-mist px-4 py-3 text-sm">
                    {COLUMNS.map((col) => (
                      <div key={col.key}>
                        <p className="text-xs uppercase tracking-wider text-haze">
                          {col.label}
                        </p>
                        <p className="font-mono font-tabular text-graphite">
                          {formatValue(p[col.key] as number | undefined)}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
