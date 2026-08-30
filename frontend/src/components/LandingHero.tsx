import { motion } from "framer-motion";
import { CitySearch } from "./CitySearch";
import { ContourMotif } from "./ContourMotif";

interface LandingHeroProps {
  onSubmit: (city: string) => void;
  isLoading: boolean;
}

export function LandingHero({ onSubmit, isLoading }: LandingHeroProps) {
  return (
    <section className="relative overflow-hidden">
      <ContourMotif
        className="pointer-events-none absolute inset-0 h-full w-full text-instrument"
        opacity={0.08}
      />

      <div className="relative mx-auto flex min-h-[70vh] max-w-3xl flex-col justify-center px-6 py-24">
        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="font-display text-4xl leading-tight text-graphite sm:text-5xl"
        >
          Understand the air
          <br />
          around you.
        </motion.h1>

        <p className="mt-6 max-w-xl text-[15px] leading-relaxed text-haze">
          Explore AQI, pollution trends, major pollution events, and
          historical air-quality patterns for any supported city.
        </p>

        <div className="mt-10 max-w-xl">
          <CitySearch onSubmit={onSubmit} isLoading={isLoading} />
        </div>

        <p className="mt-4 text-xs text-haze">
          Analyze a city using available air-quality observations.
        </p>
      </div>
    </section>
  );
}
