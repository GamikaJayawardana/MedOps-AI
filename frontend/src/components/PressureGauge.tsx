import {
  LEVEL_HEX,
  LEVEL_LABEL,
  pct,
  pressureLevel,
} from "@/lib/telemetry-utils";

interface PressureGaugeProps {
  /** hospital_pressure 0.0 – 1.0, or null before first telemetry. */
  pressure: number | null;
}

const CX = 100;
const CY = 100;
const R = 78;
const TRACK_WIDTH = 12;

/** Round to 3dp so server and client render byte-identical SVG (no hydration
 *  mismatch from floating-point non-determinism in Math.cos/sin). */
const r3 = (n: number) => Math.round(n * 1000) / 1000;

/** Map a 0–1 value to a point on the top semicircle (180° → 0°). */
function pointOnArc(value: number, radius: number) {
  const angle = (180 - value * 180) * (Math.PI / 180);
  return {
    x: r3(CX + radius * Math.cos(angle)),
    y: r3(CY - radius * Math.sin(angle)),
  };
}

/** SVG path for the arc between two 0–1 values along the top semicircle. */
function arcPath(from: number, to: number, radius: number) {
  const start = pointOnArc(from, radius);
  const end = pointOnArc(to, radius);
  return `M ${start.x} ${start.y} A ${radius} ${radius} 0 0 1 ${end.x} ${end.y}`;
}

/** Coloured zones along the dial, matching the ward colour thresholds. */
const ZONES: Array<{ from: number; to: number; hex: string }> = [
  { from: 0, to: 0.75, hex: LEVEL_HEX.calm },
  { from: 0.75, to: 0.9, hex: LEVEL_HEX.busy },
  { from: 0.9, to: 1, hex: LEVEL_HEX.critical },
];

/**
 * The overall hospital-pressure instrument: an analog manometer dial.
 * A calm accent needle sweeps across green/amber/red zones — the dial itself
 * is the alerting mechanism, so it reads at a glance from across a room.
 */
export function PressureGauge({ pressure }: PressureGaugeProps) {
  const value = pressure ?? 0;
  const clamped = Math.min(1, Math.max(0, value));
  const level = pressureLevel(clamped);
  const needle = pointOnArc(clamped, R - 6);
  const hasValue = pressure !== null;

  // Minor ticks every 0.1 across the dial.
  const ticks = Array.from({ length: 11 }, (_, i) => i / 10);

  return (
    <div className="flex flex-col items-center px-4 pb-5 pt-2">
      <svg
        viewBox="0 0 200 128"
        className="w-full max-w-[280px]"
        role="img"
        aria-label={
          hasValue
            ? `Hospital pressure ${pct(clamped)}, ${LEVEL_LABEL[level]}`
            : "Hospital pressure, awaiting data"
        }
      >
        {/* Base track */}
        <path
          d={arcPath(0, 1, R)}
          fill="none"
          stroke="var(--color-hairline)"
          strokeWidth={TRACK_WIDTH}
          strokeLinecap="round"
        />
        {/* Coloured zones */}
        {ZONES.map((zone) => (
          <path
            key={zone.from}
            d={arcPath(zone.from, zone.to, R)}
            fill="none"
            stroke={zone.hex}
            strokeWidth={TRACK_WIDTH}
            strokeLinecap="butt"
            opacity={hasValue ? 0.28 : 0.16}
          />
        ))}
        {/* Active fill up to the current value */}
        {hasValue && clamped > 0 && (
          <path
            d={arcPath(0, clamped, R)}
            fill="none"
            stroke={LEVEL_HEX[level]}
            strokeWidth={TRACK_WIDTH}
            strokeLinecap="round"
            style={{ transition: "stroke 0.5s ease" }}
          />
        )}
        {/* Tick marks */}
        {ticks.map((t) => {
          const outer = pointOnArc(t, R + TRACK_WIDTH / 2 + 3);
          const inner = pointOnArc(t, R + TRACK_WIDTH / 2 - 1);
          return (
            <line
              key={t}
              x1={inner.x}
              y1={inner.y}
              x2={outer.x}
              y2={outer.y}
              stroke="var(--color-muted)"
              strokeWidth={t * 10 === 5 ? 1.5 : 1}
              opacity={0.4}
            />
          );
        })}
        {/* Needle */}
        {hasValue && (
          <g style={{ transition: "transform 0.6s cubic-bezier(0.22,1,0.36,1)" }}>
            <line
              x1={CX}
              y1={CY}
              x2={needle.x}
              y2={needle.y}
              stroke={LEVEL_HEX[level]}
              strokeWidth={3}
              strokeLinecap="round"
            />
            <circle cx={CX} cy={CY} r={7} fill="var(--color-surface)" />
            <circle
              cx={CX}
              cy={CY}
              r={5}
              fill={LEVEL_HEX[level]}
              style={{ transition: "fill 0.5s ease" }}
            />
          </g>
        )}
      </svg>

      {/* Digital readout beneath the analog dial */}
      <div className="-mt-3 flex flex-col items-center">
        <div className="tnum text-4xl font-semibold leading-none text-ink">
          {hasValue ? pct(clamped) : "—"}
        </div>
        <div
          className="mt-2 text-xs font-semibold uppercase tracking-[0.14em]"
          style={{ color: hasValue ? LEVEL_HEX[level] : "var(--color-muted)" }}
        >
          {hasValue ? LEVEL_LABEL[level] : "Standby"}
        </div>
      </div>
    </div>
  );
}
