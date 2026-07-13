import type { WardTelemetry } from "@/lib/types";
import {
  LEVEL_CLASSES,
  LEVEL_HEX,
  LEVEL_LABEL,
  occupancyLevel,
  pct,
  wardLabel,
} from "@/lib/telemetry-utils";

interface WardCardProps {
  ward: WardTelemetry;
}

interface StatProps {
  label: string;
  value: string | number;
  emphasise?: boolean;
}

function Stat({ label, value, emphasise = false }: StatProps) {
  return (
    <div className="flex flex-col">
      <span className="text-[0.65rem] font-medium uppercase tracking-wide text-muted">
        {label}
      </span>
      <span
        className={`tnum text-base font-semibold ${
          emphasise ? "text-critical" : "text-ink"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

/**
 * One ward tile. Colour-coded by occupancy: a status rail on the left plus a
 * tinted occupancy bar. Zero available beds is flagged red as a hard signal.
 */
export function WardCard({ ward }: WardCardProps) {
  const level = occupancyLevel(ward.occupancy_rate);
  const cls = LEVEL_CLASSES[level];
  const occupancyWidth = `${Math.min(100, Math.round(ward.occupancy_rate * 100))}%`;

  return (
    <article
      className="relative overflow-hidden rounded-xl border border-hairline bg-surface p-4 shadow-[0_1px_2px_rgba(15,23,42,0.04)] transition-shadow duration-300 hover:shadow-[0_4px_12px_rgba(15,23,42,0.06)]"
      aria-label={`${wardLabel(ward.ward)} ward, occupancy ${pct(
        ward.occupancy_rate,
      )}, ${LEVEL_LABEL[level]}`}
    >
      {/* Status rail */}
      <span
        aria-hidden="true"
        className={`absolute inset-y-0 left-0 w-1 ${cls.dot}`}
        style={{ transition: "background-color 0.4s ease" }}
      />

      <div className="mb-3 flex items-start justify-between gap-2 pl-1">
        <h3 className="text-sm font-semibold text-ink">
          {wardLabel(ward.ward)}
        </h3>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[0.65rem] font-semibold ${cls.text} ${cls.bg} ${cls.border}`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${cls.dot}`} />
          {LEVEL_LABEL[level]}
        </span>
      </div>

      {/* Occupancy headline + bar */}
      <div className="mb-3 pl-1">
        <div className="flex items-baseline gap-2">
          <span className="tnum text-3xl font-semibold leading-none text-ink">
            {pct(ward.occupancy_rate)}
          </span>
          <span className="text-xs text-muted">occupied</span>
        </div>
        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-canvas">
          <div
            className="h-full rounded-full"
            style={{
              width: occupancyWidth,
              backgroundColor: LEVEL_HEX[level],
              transition: "width 0.5s ease, background-color 0.4s ease",
            }}
          />
        </div>
      </div>

      {/* Vitals grid */}
      <div className="grid grid-cols-3 gap-2 pl-1">
        <Stat
          label="Beds"
          value={ward.available_beds}
          emphasise={ward.available_beds === 0}
        />
        <Stat label="Staff" value={ward.staff_on_shift} />
        <Stat label="Influx" value={ward.patient_influx} />
      </div>
    </article>
  );
}
