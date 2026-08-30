/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        overcast: "#F5F6F4",
        graphite: "#15181B",
        haze: "#6B7178",
        mist: "#E4E6E2",
        instrument: {
          DEFAULT: "#2C4A6E",
          light: "#3D6288",
        },
        aqi: {
          good: "#2E9E5B",
          satisfactory: "#4FAE9B",
          moderate: "#D9A62E",
          poor: "#DB7C2E",
          verypoor: "#C5502F",
          severe: "#8E2A2A",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "monospace"],
        body: ["'Public Sans'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      backgroundImage: {
        contour: "url('/contour.svg')",
      },
    },
  },
  plugins: [],
};
