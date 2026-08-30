import { FormEvent, useState } from "react";
import { Input } from "./ui/Input";
import { Button } from "./ui/Button";

interface CitySearchProps {
  onSubmit: (city: string) => void;
  isLoading: boolean;
  initialValue?: string;
  compact?: boolean;
}

export function CitySearch({
  onSubmit,
  isLoading,
  initialValue = "",
  compact = false,
}: CitySearchProps) {
  const [value, setValue] = useState(initialValue);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!value.trim() || isLoading) return;
    onSubmit(value.trim());
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={compact ? "flex items-center gap-3" : "flex flex-col gap-4 sm:flex-row sm:items-end"}
      role="search"
      aria-label="Search for a city"
    >
      <div className="flex-1">
        {!compact && (
          <label htmlFor="city-input" className="mb-1 block text-xs uppercase tracking-widest text-haze">
            City
          </label>
        )}
        <Input
          id="city-input"
          type="text"
          placeholder="Enter a city..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={isLoading}
          aria-label="City name"
        />
      </div>
      <Button type="submit" disabled={isLoading || !value.trim()}>
        {isLoading ? "Analyzing…" : "Analyze"}
      </Button>
    </form>
  );
}
