import {
  AQIHeroSkeleton,
  ChartSkeleton,
  GridSkeleton,
  ListSkeleton,
  RowSkeleton,
} from "./Skeletons";

export function ReportSkeleton() {
  return (
    <div className="mx-auto max-w-6xl divide-y divide-mist/70 px-6">
      <AQIHeroSkeleton />
      <div className="py-4">
        <RowSkeleton />
      </div>
      <div className="py-8">
        <GridSkeleton />
      </div>
      <div className="py-8">
        <ChartSkeleton />
      </div>
      <div className="py-8">
        <ListSkeleton />
      </div>
    </div>
  );
}
