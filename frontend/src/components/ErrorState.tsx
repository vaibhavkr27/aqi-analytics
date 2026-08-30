export function ErrorState({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="mx-auto max-w-6xl border border-aqi-poor/30 bg-aqi-poor/5 px-6 py-4 text-sm text-graphite"
    >
      {message}
    </div>
  );
}
