# AeroIQ — Frontend

A premium, distinctive frontend for the AeroIQ air-quality intelligence
platform. This is **frontend only** — it talks to your existing FastAPI
backend and does not create, replace, or assume any backend/database.

## Stack

React + TypeScript + Vite + Tailwind CSS + Recharts + Framer Motion.

## Getting started

```bash
npm install
cp .env.example .env   # adjust VITE_API_BASE_URL if your backend runs elsewhere
npm run dev
```

Then open the printed local URL (usually `http://localhost:5173`).

Your FastAPI backend must be running and reachable at the URL in `.env`
(default `http://127.0.0.1:8000`), serving:

```
GET /api/report?city={encodedCity}
```

### CORS

If you see a network/CORS error in the browser console, your FastAPI backend
needs `CORSMiddleware` configured to allow requests from the frontend's dev
origin (e.g. `http://localhost:5173`). That's a backend-side change — nothing
in this frontend can work around a CORS block.

## Building for production

```bash
npm run build
```

Output goes to `dist/`. Preview it locally with `npm run preview`.

## Project structure

```
src/
  api/aeroiq.ts        # the ONLY file that talks to the network
  lib/aqi.ts            # formatting + AQI category color helpers
  components/
    ui/                  # restyled primitives (Button, Input)
    ContourMotif.tsx      # the signature contour-line visual motif
    AQIHero.tsx           # primary AQI hero + gauge
    QuickStats.tsx
    PollutantBreakdown.tsx   # "What's driving the AQI?"
    PollutantSummary.tsx     # 30-day pollution profile table
    TrendChart.tsx / TrendSection.tsx
    HourlyPattern.tsx
    DailyPattern.tsx
    PollutionEvents.tsx      # anomalies + top peaks
    WeekdayWeekend.tsx
    DataCoverage.tsx
    InsightsPanel.tsx
    ReportSummary.tsx
    LandingHero.tsx / ReportSkeleton.tsx / ErrorState.tsx
  App.tsx                # orchestrates state + section layout
```

## Design system

- **Colors:** Overcast (#F5F6F4) background, Graphite (#15181B) text, Haze
  (#6B7178) secondary text, Mist (#E4E6E2) borders, Instrument Blue (#2C4A6E)
  as the one accent. AQI category colors (green → deep red) are reserved
  strictly for status badges, chart markers, and alerts.
- **Type:** Space Grotesk for the AQI number and headlines, Public Sans for
  body text, IBM Plex Mono for every tabular figure (tables, timestamps,
  stats).
- **Signature element:** a faint contour-line ("isopleth") pattern behind the
  AQI hero, echoed once more behind the hourly-pattern section — a nod to how
  atmospheric scientists actually map concentration gradients.

## Notes

- Every field from the backend is treated as potentially missing — pollutants
  with insufficient data show "Insufficient data" rather than a fake zero.
- No city is ever hardcoded; the entire UI is driven by whatever the API
  returns for the searched city.
- All insight text (`insights.*`) is rendered verbatim from the backend —
  these are the human-readable strings your `insights.py` module generates.
