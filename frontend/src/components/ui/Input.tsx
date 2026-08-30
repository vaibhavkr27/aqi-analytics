import { InputHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

export const Input = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={clsx(
        "w-full bg-transparent border-b border-mist px-1 py-3 text-lg text-graphite placeholder:text-haze",
        "focus:outline-none focus:border-instrument transition-colors",
        className,
      )}
      {...props}
    />
  );
});

Input.displayName = "Input";
