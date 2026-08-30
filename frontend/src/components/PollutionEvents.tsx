import { Anomaly, PollutionPeak } from "../api/aeroiq";
import { formatDateTime, formatDeviation, formatValue, parameterLabel } from "../lib/aqi";

interface PollutionEventsProps {
  anomalies: Anomaly[];
  peaks: PollutionPeak[];
}

function validAnomalies(anomalies: Anomaly[]): Anomaly[] {
  // Ignore unreliable zero/negative-baseline anomalies (e.g. some CO
  // readings) and non-positive deviations, which aren't genuine spikes.
  return anomalies.filter(
    (a) =>
      a.local_median !== null &&
      a.local_median > 0 &&
      a.deviation_percent !== null &&
      a.deviation_percent > 0,
  );
}

export function PollutionEvents({ anomalies, peaks }: PollutionEventsProps) {
  const events = validAnomalies(anomalies).sort(
    (a, b) => (b.deviation_percent ?? 0) - (a.deviation_percent ?? 0),
  );

  return (
    <section id="events" className="border-b border-mist/70">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Events</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          Significant pollution events
        </h2>

        {events.length ? (
          <ol className="mt-8 space-y-6 border-l border-mist pl-6">
            {events.map((event, i) => (
              <li key={i} className="relative">
                <span
                  className="absolute -left-[29px] top-1.5 h-2 w-2 rounded-full bg-aqi-poor"
                  aria-hidden="true"
                />
                <p className="font-medium text-graphite">
                  {parameterLabel(event.parameter)}
                </p>
                <p className="mt-1 font-mono font-tabular text-2xl text-graphite">
                  {formatValue(event.value)}
                  <span className="ml-1 text-sm text-haze">{event.unit ?? ""}</span>
                </p>
                <p className="mt-1 text-sm text-haze">
                  {formatDateTime(event.timestamp)}
                </p>
                <p className="mt-1 text-sm font-medium text-aqi-poor">
                  {formatDeviation(event.deviation_percent)} vs local baseline
                  {event.local_median != null &&
                    ` of ${formatValue(event.local_median)} ${event.unit ?? ""}`}
                </p>
              </li>
            ))}
          </ol>
        ) : (
          <p className="mt-8 text-sm italic text-haze">
            No statistically significant pollution events were detected in
            this window.
          </p>
        )}

        {peaks.length > 0 && (
          <div className="mt-16">
            <h3 className="font-display text-lg text-graphite">
              Top pollution peaks
            </h3>
            <ul className="mt-4 space-y-3">
              {peaks.slice(0, 10).map((peak, i) => (
                <li
                  key={i}
                  className="flex flex-wrap items-baseline justify-between gap-2 border-b border-mist/60 py-2 text-sm"
                >
                  <span className="text-graphite">
                    {parameterLabel(peak.parameter)} reached{" "}
                    <span className="font-mono font-tabular">
                      {formatValue(peak.value)} {peak.unit ?? ""}
                    </span>
                  </span>
                  <span className="text-haze">{formatDateTime(peak.timestamp)}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
