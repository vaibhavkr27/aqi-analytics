import { useState } from "react";
import { AeroIQError, CityReport, getCityReport } from "./api/aeroiq";
import { Header } from "./components/Header";
import { LandingHero } from "./components/LandingHero";
import { CitySearch } from "./components/CitySearch";
import { ReportSkeleton } from "./components/ReportSkeleton";
import { ErrorState } from "./components/ErrorState";
import { AQIHero } from "./components/AQIHero";
import { QuickStats } from "./components/QuickStats";
import { PollutantBreakdown } from "./components/PollutantBreakdown";
import { PollutantSummary } from "./components/PollutantSummary";
import { TrendSection } from "./components/TrendSection";
import { HourlyPattern } from "./components/HourlyPattern";
import { DailyPattern } from "./components/DailyPattern";
import { PollutionEvents } from "./components/PollutionEvents";
import { WeekdayWeekend } from "./components/WeekdayWeekend";
import { DataCoverage } from "./components/DataCoverage";
import { InsightsPanel } from "./components/InsightsPanel";
import { ReportSummary } from "./components/ReportSummary";

type Status = "idle" | "loading" | "error" | "success";

export default function App() {
  const [status, setStatus] = useState<Status>("idle");
  const [report, setReport] = useState<CityReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastQuery, setLastQuery] = useState("");

  async function handleSearch(city: string) {
    setStatus("loading");
    setErrorMessage(null);
    setLastQuery(city);

    try {
      const result = await getCityReport(city);
      setReport(result);
      setStatus("success");
    } catch (err) {
      const message =
        err instanceof AeroIQError
          ? err.message
          : "Something went wrong while analyzing this city.";
      setErrorMessage(message);
      setStatus("error");
    }
  }

  const isLoading = status === "loading";
  const showResults = status === "success" && report;

  return (
    <div id="top" className="min-h-screen bg-overcast">
      <Header showNav={Boolean(showResults)} />

      {status === "idle" && (
        <LandingHero onSubmit={handleSearch} isLoading={isLoading} />
      )}

      {status !== "idle" && (
        <div className="mx-auto max-w-6xl px-6 py-10">
          <CitySearch
            onSubmit={handleSearch}
            isLoading={isLoading}
            initialValue={lastQuery}
            compact
          />
        </div>
      )}

      {status === "loading" && <ReportSkeleton />}

      {status === "error" && errorMessage && (
        <div className="px-6">
          <ErrorState message={errorMessage} />
        </div>
      )}

      {showResults && report && (
        <main>
          <AQIHero city={report.city} aqi={report.analytics.aqi} />
          <QuickStats report={report} />
          <PollutantBreakdown subindices={report.analytics.aqi?.subindices ?? []} />
          <PollutantSummary pollutants={report.analytics.pollutant_statistics} />
          <TrendSection dailyTrends={report.analytics.daily_trends} />
          <HourlyPattern
            hourlyPatterns={report.analytics.hourly_patterns}
            hourlyExtremes={report.analytics.hourly_extremes}
          />
          <DailyPattern
            dailyExtremes={report.analytics.daily_extremes}
            dailyTrends={report.analytics.daily_trends}
          />
          <PollutionEvents
            anomalies={report.analytics.anomalies}
            peaks={report.analytics.pollution_peaks}
          />
          <WeekdayWeekend data={report.analytics.weekday_weekend} />
          <DataCoverage rows={report.analytics.data_coverage} />
          <InsightsPanel insights={report.insights} />
          <ReportSummary report={report} />
        </main>
      )}

      <footer className="mx-auto max-w-6xl px-6 py-10 text-xs text-haze">
        AeroIQ — air quality intelligence, built on available observations.
      </footer>
    </div>
  );
}
