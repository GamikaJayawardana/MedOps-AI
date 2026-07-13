/**
 * Wire types for the MedOps AI telemetry WebSocket.
 *
 * These mirror the FastAPI backend contract exactly (server → client and
 * client → server). Keep this file the single source of truth for message
 * shapes so components never reach for `any`.
 */

/** Known wards, kept as a union for autocomplete but widened to string in the
 *  wire types so an unexpected ward from the backend never breaks rendering. */
export type KnownWard = "respiratory" | "cardiology" | "general" | "pediatric";

export type RiskLevel = "LOW" | "MODERATE" | "HIGH";

export type ComplianceStatus = "approved" | "rejected" | "needs_review";

export type StaffAction = "add" | "remove";

/** Live connection lifecycle surfaced to the UI. */
export type ConnectionStatus = "connecting" | "connected" | "closed" | "error";

/** A single ward's live vitals. */
export interface WardTelemetry {
  ward: string;
  patient_influx: number;
  available_beds: number;
  staff_on_shift: number;
  /** 0.0 – 1.0 */
  occupancy_rate: number;
}

/** One telemetry snapshot for the whole hospital. */
export interface Telemetry {
  timestamp: string;
  /** 0.0 – 1.0 */
  hospital_pressure: number;
  wards: WardTelemetry[];
}

/** A single proposed staffing change within a plan. */
export interface PlanChange {
  ward: string;
  action: StaffAction;
  staff_delta: number;
  reason: string;
}

/** The AI's proposed reallocation plan (may be null when no action is needed). */
export interface Plan {
  summary: string;
  changes: PlanChange[];
}

/** The regulatory/compliance verdict on a plan (may be null). */
export interface Compliance {
  status: ComplianceStatus;
  violations: string[];
  reasoning: string;
}

/** The full analysis payload produced by the multi-agent graph. */
export interface AnalysisResult {
  thread_id: string;
  risk_level: RiskLevel;
  triage_assessment: string;
  resource_recommendation: string;
  /** When true, the graph is paused and the plan needs human approval. */
  awaiting_approval: boolean;
  committed: boolean;
  plan: Plan | null;
  compliance: Compliance | null;
}

/* ------------------------------------------------------------------ */
/* Server → client messages                                            */
/* ------------------------------------------------------------------ */

export interface TelemetryMessage {
  type: "telemetry";
  data: Telemetry;
}

export interface AnalysisStartedMessage {
  type: "analysis_started";
  reason: "auto" | "manual";
}

export interface AnalysisResultMessage {
  type: "analysis_result";
  data: AnalysisResult;
}

export type ServerMessage =
  | TelemetryMessage
  | AnalysisStartedMessage
  | AnalysisResultMessage;

/* ------------------------------------------------------------------ */
/* Client → server messages                                            */
/* ------------------------------------------------------------------ */

export interface AnalyseCommand {
  action: "analyse";
}

export interface ApproveCommand {
  action: "approve";
  thread_id: string;
}

export type ClientMessage = AnalyseCommand | ApproveCommand;

/* ------------------------------------------------------------------ */
/* Derived UI types                                                    */
/* ------------------------------------------------------------------ */

/** One flattened point in the rolling chart history. Ward occupancies are
 *  keyed by ward name alongside the fixed fields, hence the index signature. */
export interface HistoryPoint {
  /** epoch milliseconds — used for ordering and the x-axis */
  t: number;
  /** short HH:MM:SS label for the axis */
  label: string;
  /** hospital pressure 0.0 – 1.0 */
  pressure: number;
  [ward: string]: number | string;
}

/** Occupancy severity buckets driving the ward colour-coding. */
export type OccupancyLevel = "calm" | "busy" | "critical";
