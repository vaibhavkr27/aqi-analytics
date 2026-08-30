interface ContourMotifProps {
  className?: string;
  opacity?: number;
}

/**
 * Faint nested open contour lines, evoking the isopleth maps used in
 * atmospheric science to visualize concentration gradients. This is
 * AeroIQ's one signature visual element — do not reuse it as generic
 * decoration outside AQIHero and HourlyPattern.
 */
export function ContourMotif({ className = "", opacity = 1 }: ContourMotifProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 800 400"
      fill="none"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
      style={{ opacity }}
    >
      <path
        d="M -50 320 C 150 280, 250 340, 400 300 S 650 220, 850 260"
        stroke="currentColor"
        strokeWidth="1"
      />
      <path
        d="M -50 260 C 170 220, 260 280, 420 240 S 660 160, 850 200"
        stroke="currentColor"
        strokeWidth="1"
      />
      <path
        d="M -50 200 C 190 160, 280 220, 440 180 S 670 100, 850 140"
        stroke="currentColor"
        strokeWidth="1"
      />
      <path
        d="M -50 140 C 210 100, 300 160, 460 120 S 680 40, 850 80"
        stroke="currentColor"
        strokeWidth="1"
      />
    </svg>
  );
}
