import { categoryColorClass } from "../lib/aqi";

export function AQIStatus({ category }: { category: string | null | undefined }) {
  const colors = categoryColorClass(category);

  return (
    <span
      className={`inline-flex items-center gap-1.5 border px-2.5 py-1 text-xs font-medium uppercase tracking-wider ${colors.text} ${colors.bg} ${colors.border}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {category ?? "Unknown"}
    </span>
  );
}
