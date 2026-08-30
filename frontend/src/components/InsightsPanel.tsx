import { Insights } from "../api/aeroiq";

const CATEGORY_TITLES: Record<keyof Insights, string> = {
  pollution_spikes: "Pollution spikes",
  peak_concentrations: "Top pollution peaks",
  hourly_patterns: "Hourly patterns",
  daily_patterns: "Daily patterns",
};

export function InsightsPanel({ insights }: { insights: Insights }) {
  const categories = Object.keys(CATEGORY_TITLES) as (keyof Insights)[];
  const hasAny = categories.some((c) => insights[c]?.length);

  if (!hasAny) return null;

  return (
    <section className="border-b border-mist/70">
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-haze">Insights</p>
        <h2 className="mt-2 font-display text-2xl text-graphite">
          What's happening?
        </h2>

        <div className="mt-10 space-y-10">
          {categories.map((category) => {
            const items = insights[category];
            if (!items?.length) return null;

            return (
              <div key={category}>
                <h3 className="text-xs uppercase tracking-widest text-haze">
                  {CATEGORY_TITLES[category]}
                </h3>
                <ul className="mt-3 space-y-4">
                  {items.map((text, i) => (
                    <li
                      key={i}
                      className="border-l-2 border-instrument/30 pl-4 text-[15px] leading-relaxed text-graphite"
                    >
                      {text}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
