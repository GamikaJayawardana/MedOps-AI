"use client";

import { useMemo } from "react";
import { useTelemetry } from "@/lib/useTelemetry";
import { clockLabel, occupancyLevel } from "@/lib/telemetry-utils";
import { ConnectionStatus } from "./ConnectionStatus";
import { PressureGauge } from "./PressureGauge";
import { WardGrid } from "./WardGrid";
import { TelemetryChart } from "./TelemetryChart";
import { AnalyseButton } from "./AnalyseButton";
import { ApprovalModal } from "./ApprovalModal";
import { Panel } from "./Panel";

/** Small labelled figure used in the fleet-overview strip. */
function OverviewStat({
  label,
  value,
  tone = "ink",
}: {
  label: string;
  value: string | number;
  tone?: "ink" | "critical";
}) {
  return (
    <div className="flex flex-col items-center">
      <span
        className={`tnum text-xl font-semibold ${
          tone === "critical" ? "text-critical" : "text-ink"
        }`}
      >
        {value}
      </span>
      <span className="mt-0.5 text-[0.65rem] font-medium uppercase tracking-wide text-muted">
        {label}
      </span>
    </div>
  );
}

/** MedOps AI cross mark — a calm, custom logo for the control centre. */
function LogoMark() {
  return (
    <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-white shadow-sm">
      <svg
        viewBox="0 0 24 24"
        className="h-5 w-5"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M3 12h4l2-5 3 10 2-5h4" />
      </svg>
    </span>
  );
}

/**
 * The MedOps AI control centre. Owns the telemetry connection and lays out the
 * gauge, live chart, ward grid, manual-analysis control, and approval modal.
 */
export function Dashboard() {
  const {
    status,
    telemetry,
    history,
    analysis,
    analysisRunning,
    hasData,
    requestAnalysis,
    approvePlan,
    dismissAnalysis,
  } = useTelemetry();

  const wardOrder = useMemo(
    () => telemetry?.wards.map((w) => w.ward) ?? [],
    [telemetry],
  );

  const overview = useMemo(() => {
    if (!telemetry) return null;
    return {
      beds: telemetry.wards.reduce((sum, w) => sum + w.available_beds, 0),
      staff: telemetry.wards.reduce((sum, w) => sum + w.staff_on_shift, 0),
      critical: telemetry.wards.filter(
        (w) => occupancyLevel(w.occupancy_rate) === "critical",
      ).length,
    };
  }, [telemetry]);

  const showModal =
    analysis !== null && (analysis.awaiting_approval || analysis.committed);

  return (
    <div className="mx-auto flex w-full max-w-[1400px] flex-1 flex-col px-4 py-4 sm:px-6 sm:py-6">
      {/* Header */}
      <header className="mb-4 flex flex-col gap-3 sm:mb-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <LogoMark />
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-ink sm:text-xl">
              MedOps <span className="text-accent">AI</span>
            </h1>
            <p className="text-xs text-muted">Hospital Operations Control Centre</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="tnum hidden text-xs text-muted sm:inline">
            {telemetry ? `Updated ${clockLabel(telemetry.timestamp)}` : "—"}
          </span>
          <ConnectionStatus status={status} />
          <AnalyseButton
            onAnalyse={requestAnalysis}
            running={analysisRunning}
            disabled={status !== "connected"}
          />
        </div>
      </header>

      {/* Primary grid */}
      <div className="grid flex-1 grid-cols-1 gap-4 xl:grid-cols-12">
        {/* Pressure instrument */}
        <Panel
          title="Hospital Pressure"
          className="flex min-w-0 flex-col xl:col-span-4"
        >
          <PressureGauge pressure={telemetry?.hospital_pressure ?? null} />
          <div className="mt-auto grid grid-cols-3 gap-2 border-t border-hairline px-4 py-4">
            <OverviewStat label="Beds free" value={overview?.beds ?? "—"} />
            <OverviewStat label="On shift" value={overview?.staff ?? "—"} />
            <OverviewStat
              label="Critical"
              value={overview?.critical ?? "—"}
              tone={overview && overview.critical > 0 ? "critical" : "ink"}
            />
          </div>
        </Panel>

        {/* Live chart */}
        <Panel className="min-w-0 xl:col-span-8">
          <TelemetryChart history={history} wards={wardOrder} />
        </Panel>

        {/* Ward grid */}
        <section className="xl:col-span-12" aria-label="Ward status">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-muted">
              Wards
            </h2>
            {!hasData && (
              <span className="text-xs text-muted">Awaiting telemetry…</span>
            )}
          </div>
          <WardGrid wards={telemetry?.wards ?? []} />
        </section>
      </div>

      {showModal && analysis && (
        <ApprovalModal
          result={analysis}
          approving={analysisRunning}
          onApprove={approvePlan}
          onDismiss={dismissAnalysis}
        />
      )}
    </div>
  );
}
