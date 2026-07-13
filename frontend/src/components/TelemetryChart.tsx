"use client";

import { useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  type TooltipContentProps,
  XAxis,
  YAxis,
} from "recharts";
import type { HistoryPoint } from "@/lib/types";
import { wardLabel } from "@/lib/telemetry-utils";

interface TelemetryChartProps {
  history: HistoryPoint[];
  /** Ward ids in a stable order, used for the occupancy series. */
  wards: string[];
}

type Mode = "pressure" | "occupancy";

/** Distinct-but-clinical hues so wards stay legible without shouting. */
const WARD_COLORS = ["#2563eb", "#0891b2", "#7c3aed", "#db2777", "#059669"];

const CHART_HEIGHT = 240;

function percentTick(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function ChartTooltip({ active, payload, label }: TooltipContentProps) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="rounded-lg border border-hairline bg-surface px-3 py-2 text-xs shadow-md">
      <div className="mb-1 font-semibold text-ink tnum">{label}</div>
      <ul className="space-y-0.5">
        {payload.map((entry, i) => (
          <li key={i} className="flex items-center gap-2">
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-muted">{entry.name}</span>
            <span className="tnum ml-auto font-semibold text-ink">
              {typeof entry.value === "number"
                ? percentTick(entry.value)
                : "—"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Live trend chart driven by the rolling history. The plotting area has a
 * fixed height so the card never shifts as data streams in (Core Web Vitals).
 */
export function TelemetryChart({ history, wards }: TelemetryChartProps) {
  const [mode, setMode] = useState<Mode>("pressure");
  const hasData = history.length > 0;

  const axisProps = useMemo(
    () => ({
      stroke: "var(--color-muted)",
      tick: { fontSize: 11, fill: "var(--color-muted)" },
      tickLine: false,
      axisLine: false,
    }),
    [],
  );

  return (
    <div className="min-w-0">
      <div className="flex items-center justify-between px-4 pt-4 sm:px-5">
        <div>
          <h2 className="text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-muted">
            Live Trend
          </h2>
          <p className="mt-0.5 text-xs text-muted">
            {mode === "pressure"
              ? "Hospital pressure over time"
              : "Ward occupancy over time"}
          </p>
        </div>
        <div
          className="inline-flex rounded-lg border border-hairline bg-canvas p-0.5"
          role="tablist"
          aria-label="Chart metric"
        >
          {(["pressure", "occupancy"] as const).map((m) => (
            <button
              key={m}
              type="button"
              role="tab"
              aria-selected={mode === m}
              onClick={() => setMode(m)}
              className={`rounded-md px-3 py-1 text-xs font-semibold capitalize transition-colors ${
                mode === m
                  ? "bg-surface text-accent shadow-sm"
                  : "text-muted hover:text-ink"
              }`}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Fixed-height plot area reserves space to prevent layout shift.
          min-w-0 + overflow-hidden let recharts shrink instead of forcing
          horizontal overflow when the panel narrows. */}
      <div
        className="relative min-w-0 overflow-hidden px-2 pb-3 pt-2"
        style={{ height: CHART_HEIGHT + 16 }}
      >
        {!hasData && (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-sm text-muted">Waiting for telemetry…</p>
          </div>
        )}
        <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
          {mode === "pressure" ? (
            <AreaChart
              data={history}
              margin={{ top: 8, right: 12, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="pressureFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2563eb" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#2563eb" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-hairline)"
                vertical={false}
              />
              <XAxis
                dataKey="label"
                minTickGap={40}
                {...axisProps}
              />
              <YAxis
                domain={[0, 1]}
                width={40}
                tickFormatter={percentTick}
                {...axisProps}
              />
              <ReferenceLine
                y={0.9}
                stroke="#dc2626"
                strokeDasharray="4 4"
                strokeOpacity={0.5}
              />
              <Tooltip content={(props) => <ChartTooltip {...props} />} />
              <Area
                type="monotone"
                dataKey="pressure"
                name="Pressure"
                stroke="#2563eb"
                strokeWidth={2}
                fill="url(#pressureFill)"
                isAnimationActive={false}
                dot={false}
              />
            </AreaChart>
          ) : (
            <LineChart
              data={history}
              margin={{ top: 8, right: 12, left: 0, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-hairline)"
                vertical={false}
              />
              <XAxis dataKey="label" minTickGap={40} {...axisProps} />
              <YAxis
                domain={[0, 1]}
                width={40}
                tickFormatter={percentTick}
                {...axisProps}
              />
              <Tooltip content={(props) => <ChartTooltip {...props} />} />
              {wards.map((ward, i) => (
                <Line
                  key={ward}
                  type="monotone"
                  dataKey={ward}
                  name={wardLabel(ward)}
                  stroke={WARD_COLORS[i % WARD_COLORS.length]}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>

      {mode === "occupancy" && wards.length > 0 && (
        <div className="flex flex-wrap gap-x-4 gap-y-1 px-4 pb-4 sm:px-5">
          {wards.map((ward, i) => (
            <span
              key={ward}
              className="inline-flex items-center gap-1.5 text-xs text-muted"
            >
              <span
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: WARD_COLORS[i % WARD_COLORS.length] }}
              />
              {wardLabel(ward)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
