import type { RiskLevel } from "@/lib/types";

interface RiskBadgeProps {
  level: RiskLevel;
  size?: "sm" | "md";
}

const RISK_STYLES: Record<RiskLevel, string> = {
  LOW: "text-calm bg-calm/10 border-calm/30",
  MODERATE: "text-busy bg-busy/10 border-busy/30",
  HIGH: "text-critical bg-critical/10 border-critical/40",
};

const RISK_DOT: Record<RiskLevel, string> = {
  LOW: "bg-calm",
  MODERATE: "bg-busy",
  HIGH: "bg-critical",
};

/** Coloured risk-level pill used in the header and approval modal. */
export function RiskBadge({ level, size = "md" }: RiskBadgeProps) {
  const pad = size === "sm" ? "px-2 py-0.5 text-[0.65rem]" : "px-3 py-1 text-xs";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-semibold uppercase tracking-wide ${pad} ${RISK_STYLES[level]}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${RISK_DOT[level]}`} />
      {level} risk
    </span>
  );
}
