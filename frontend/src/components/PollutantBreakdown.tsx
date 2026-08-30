import { AqiSubindex } from "../api/aeroiq";
import { AQIStatus } from "./AQIStatus";
import { formatValue } from "../lib/aqi";

interface PollutantBreakdownProps {
  subindices: AqiSubindex[];
}

const ALL_PARAMETERS = ["pm25", "pm10", "no2", "so2", "co", "o3"];

export function PollutantBreakdown({ subindices }: PollutantBreakdownProps) {
  const byParameter = new Map(subindices.map((s) => [s.parameter, s]));

  return (
    <section id="pollutants" className="border-b border-mist/70">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Drivers</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          What's driving the AQI?
        </h2>
        <p className="mt-2 max-w-xl text-sm text-haze">
          Pollutant-level contribution based on the available AQI sub-indices.
        </p>

        <div className="mt-10 grid grid-cols-1 gap-px bg-mist sm:grid-cols-2 lg:grid-cols-3">
          {ALL_PARAMETERS.map((param) => {
            const subindex = byParameter.get(param);

            return (
              <div key={param} className="bg-overcast p-6">
                <p className="font-display text-lg text-graphite">
                  {subindex?.label ?? param.toUpperCase()}
                </p>

                {subindex && subindex.status === "valid" ? (
                  <>
                    <p className="mt-2 font-mono font-tabular text-2xl text-graphite">
                      {formatValue(subindex.concentration)}
                      <span className="ml-1 text-sm text-haze">
                        {subindex.unit ?? "µg/m³"}
                      </span>
                    </p>
                    {subindex.sub_index != null && (
                      <p className="mt-1 text-sm text-haze">
                        AQI {formatValue(subindex.sub_index)}
                      </p>
                    )}
                    <div className="mt-3">
                      <AQIStatus category={subindex.category} />
                    </div>
                    <p className="mt-3 text-xs uppercase tracking-wider text-haze">
                      {subindex.averaging_hours}-hour average
                    </p>
                  </>
                ) : (
                  <p className="mt-3 text-sm italic text-haze">
                    Insufficient data for this pollutant in the current window.
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
