function Block({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-mist/60 ${className}`}
      aria-hidden="true"
    />
  );
}

export function AQIHeroSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-8 py-16 md:grid-cols-2 md:items-center">
      <div className="space-y-4">
        <Block className="h-4 w-24" />
        <Block className="h-24 w-48" />
        <Block className="h-6 w-32" />
      </div>
      <Block className="mx-auto h-64 w-64 rounded-full" />
    </div>
  );
}

export function RowSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 gap-6 py-8 sm:grid-cols-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Block className="h-3 w-20" />
          <Block className="h-6 w-16" />
        </div>
      ))}
    </div>
  );
}

export function GridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <Block key={i} className="h-28" />
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return <Block className="h-72 w-full" />;
}

export function ListSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <Block key={i} className="h-16 w-full" />
      ))}
    </div>
  );
}
