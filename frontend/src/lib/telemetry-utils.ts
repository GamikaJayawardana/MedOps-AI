import type { OccupancyLevel } from "./types";

/**
 * Map an occupancy_rate (0.0 – 1.0) to a severity bucket.
 * Thresholds per spec: <0.75 calm, 0.75–0.9 busy, >0.9 critical.
 */
export function occupancyLevel(rate: number): OccupancyLevel {
  if (rate > 0.9) return "critical";
  if (rate >= 0.75) return "busy";
  return "calm";
}

/** Hospital-pressure severity uses the same visual language as wards. */
export function pressureLevel(pressure: number): OccupancyLevel {
  if (pressure > 0.9) return "critical";
  if (pressure >= 0.75) return "busy";
  return "calm";
}

/** Canonical hex per severity — kept in sync with the CSS palette tokens.
 *  Used where inline SVG / recharts need a raw colour value. */
export const LEVEL_HEX: Record<OccupancyLevel, string> = {
  calm: "#16a34a",
  busy: "#d97706",
  critical: "#dc2626",
};

/** Tailwind-class bundles per severity, so components stay declarative. */
export const LEVEL_CLASSES: Record<
  OccupancyLevel,
  { text: string; bg: string; border: string; dot: string }
> = {
  calm: {
    text: "text-calm",
    bg: "bg-calm/10",
    border: "border-calm/30",
    dot: "bg-calm",
  },
  busy: {
    text: "text-busy",
    bg: "bg-busy/10",
    border: "border-busy/30",
    dot: "bg-busy",
  },
  critical: {
    text: "text-critical",
    bg: "bg-critical/10",
    border: "border-critical/40",
    dot: "bg-critical",
  },
};

export const LEVEL_LABEL: Record<OccupancyLevel, string> = {
  calm: "Calm",
  busy: "Busy",
  critical: "Critical",
};

/** Format a 0–1 rate as an integer percentage string, e.g. 0.96 → "96%". */
export function pct(rate: number): string {
  return `${Math.round(rate * 100)}%`;
}

/** Short clock label (HH:MM:SS) from an ISO timestamp, resilient to bad input. */
export function clockLabel(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "--:--:--";
  return d.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

/** Present a ward id as a title-cased label ("respiratory" → "Respiratory"). */
export function wardLabel(ward: string): string {
  return ward.charAt(0).toUpperCase() + ward.slice(1);
}
