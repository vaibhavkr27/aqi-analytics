interface HeaderProps {
  showNav?: boolean;
}

const NAV_LINKS = [
  { href: "#overview", label: "Overview" },
  { href: "#pollutants", label: "Pollutants" },
  { href: "#trends", label: "Trends" },
  { href: "#events", label: "Events" },
  { href: "#coverage", label: "Coverage" },
];

export function Header({ showNav = false }: HeaderProps) {
  return (
    <header className="sticky top-0 z-20 border-b border-mist/70 bg-overcast/90 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <a href="#top" className="flex flex-col leading-none">
          <span className="font-display text-sm font-semibold tracking-[0.15em] text-graphite">
            AEROIQ
          </span>
          <span className="mt-1 text-[11px] uppercase tracking-widest text-haze">
            Air quality intelligence
          </span>
        </a>

        {showNav && (
          <nav aria-label="Report sections" className="hidden gap-6 md:flex">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-sm text-haze transition-colors hover:text-graphite"
              >
                {link.label}
              </a>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
}
