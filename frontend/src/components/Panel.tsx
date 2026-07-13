import type { ReactNode } from "react";

interface PanelProps {
  children: ReactNode;
  className?: string;
  /** Optional section label rendered as an instrument-panel eyebrow. */
  title?: string;
  /** Optional element aligned to the right of the title row. */
  action?: ReactNode;
  as?: "section" | "div" | "article";
}

/**
 * A single control-centre surface: white card, hairline border, soft shadow.
 * The consistent chrome is what makes the dashboard read as one instrument.
 */
export function Panel({
  children,
  className = "",
  title,
  action,
  as: Tag = "section",
}: PanelProps) {
  return (
    <Tag
      className={`rounded-xl border border-hairline bg-surface shadow-[0_1px_2px_rgba(15,23,42,0.04)] ${className}`}
    >
      {(title || action) && (
        <header className="flex items-center justify-between gap-3 border-b border-hairline px-4 py-3 sm:px-5">
          {title && (
            <h2 className="text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-muted">
              {title}
            </h2>
          )}
          {action}
        </header>
      )}
      {children}
    </Tag>
  );
}
