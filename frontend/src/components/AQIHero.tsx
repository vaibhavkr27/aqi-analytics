import { motion } from "framer-motion";
import { AqiSummary } from "../api/aeroiq";
import { AQIStatus } from "./AQIStatus";
import { ContourMotif } from "./ContourMotif";
import { categoryColorClass, parameterLabel } from "../lib/aqi";

interface AQIHeroProps {
  city: string;
  aqi: AqiSummary | undefined;
}

function AQIGauge({ value, category }: { value: number | null; category: string | null }) {
  const colors = categoryColorClass(category);
  // AQI scale is conventionally 0-500; clamp for the arc sweep.
  const clamped = Math.max(0, Math.min(value ?? 0, 500));
  const fraction = clamped / 500;
  const radius = 90;
  const circumference = Math.PI * radius; // semicircle
  const dash = fraction * circumference;

  return (
    <svg viewBox="0 0 220 130" className="h-56 w-56 md:h-64 md:w-64">
      <path
        d="M 20 110 A 90 90 0 0 1 200 110"
        fill="none"
        stroke="currentColor"
        strokeWidth="10"
        strokeLinecap="round"
        className="text-mist"
      />
      <path
        d="M 20 110 A 90 90 0 0 1 200 110"
        fill="none"
        strokeWidth="10"
        strokeLinecap="round"
        strokeDasharray={`${dash} ${circumference}`}
        className={colors.text}
        stroke="currentColor"
      />
    </svg>
  );
}

export function AQIHero({ city, aqi }: AQIHeroProps) {
  const value = aqi?.aqi ?? null;
  const category = aqi?.category ?? null;
  const dominant = aqi?.dominant_pollutant_label ?? null;
  const colors = categoryColorClass(category);

  return (
    <section id="overview" className="relative overflow-hidden border-b border-mist/70">
      <ContourMotif
        className={`pointer-events-none absolute inset-0 h-full w-full ${colors.text}`}
        opacity={0.12}
      />

      <div className="relative mx-auto max-w-6xl px-6 py-16 md:py-24">
        <p className="text-xs uppercase tracking-widest text-haze">
          {city.toUpperCase()}
        </p>
        <p className="mt-1 text-sm text-haze">
          Air quality intelligence · Updated from available observations
        </p>

        <div className="mt-10 grid grid-cols-1 items-center gap-10 md:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          >
            <p className="text-xs uppercase tracking-widest text-haze">AQI</p>
            <p className="font-display font-tabular text-7xl leading-none text-graphite md:text-8xl">
              {value !== null ? Math.round(value) : "—"}
            </p>

            <div className="mt-4">
              <AQIStatus category={category} />
            </div>

            {dominant && (
              <p className="mt-6 text-sm text-haze">
                Dominant pollutant
                <span className="ml-2 font-medium text-graphite">
                  {dominant}
                </span>
              </p>
            )}

            <p className="mt-8 max-w-sm text-xs text-haze">
              Based on the latest available pollutant averaging windows.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
            className="flex justify-center"
          >
            <AQIGauge value={value} category={category} />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
