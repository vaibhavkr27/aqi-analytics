import { ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          "inline-flex items-center justify-center px-5 py-3 text-sm font-medium tracking-wide transition-colors",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-instrument",
          variant === "primary" &&
            "bg-instrument text-overcast hover:bg-instrument-light disabled:opacity-40",
          variant === "ghost" &&
            "bg-transparent text-graphite border border-mist hover:border-haze",
          className,
        )}
        {...props}
      />
    );
  },
);

Button.displayName = "Button";
