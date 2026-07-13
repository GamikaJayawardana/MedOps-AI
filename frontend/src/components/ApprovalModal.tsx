"use client";

import { useId } from "react";
import type {
  AnalysisResult,
  Compliance,
  ComplianceStatus,
  PlanChange,
} from "@/lib/types";
import { useFocusTrap } from "@/lib/useFocusTrap";
import { wardLabel } from "@/lib/telemetry-utils";
import { RiskBadge } from "./RiskBadge";

interface ApprovalModalProps {
  result: AnalysisResult;
  /** True while an approve command is in flight. */
  approving: boolean;
  onApprove: (threadId: string) => void;
  onDismiss: () => void;
}

const COMPLIANCE_META: Record<
  ComplianceStatus,
  { label: string; text: string; bg: string; border: string }
> = {
  approved: {
    label: "Compliant",
    text: "text-calm",
    bg: "bg-calm/10",
    border: "border-calm/30",
  },
  needs_review: {
    label: "Needs review",
    text: "text-busy",
    bg: "bg-busy/10",
    border: "border-busy/30",
  },
  rejected: {
    label: "Rejected",
    text: "text-critical",
    bg: "bg-critical/10",
    border: "border-critical/40",
  },
};

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h3 className="mb-1.5 text-[0.7rem] font-semibold uppercase tracking-[0.12em] text-muted">
        {title}
      </h3>
      {children}
    </div>
  );
}

function PlanChangeRow({ change }: { change: PlanChange }) {
  const isAdd = change.action === "add";
  return (
    <li className="flex items-start gap-3 border-t border-hairline py-2.5 first:border-t-0">
      <span
        className={`mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-sm font-bold ${
          isAdd
            ? "bg-calm/12 text-calm"
            : "bg-critical/12 text-critical"
        }`}
        aria-hidden="true"
      >
        {isAdd ? "+" : "−"}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline gap-x-2">
          <span className="text-sm font-semibold text-ink">
            {wardLabel(change.ward)}
          </span>
          <span
            className={`tnum text-sm font-semibold ${
              isAdd ? "text-calm" : "text-critical"
            }`}
          >
            {isAdd ? "+" : "−"}
            {Math.abs(change.staff_delta)} staff
          </span>
        </div>
        <p className="mt-0.5 text-xs leading-relaxed text-muted">
          {change.reason}
        </p>
      </div>
    </li>
  );
}

function CompliancePanel({ compliance }: { compliance: Compliance }) {
  const meta = COMPLIANCE_META[compliance.status];
  return (
    <div className={`rounded-lg border p-3 ${meta.border} ${meta.bg}`}>
      <div className="flex items-center gap-2">
        <span className={`text-sm font-semibold ${meta.text}`}>
          {meta.label}
        </span>
      </div>
      {compliance.reasoning && (
        <p className="mt-1.5 text-xs leading-relaxed text-ink/80">
          {compliance.reasoning}
        </p>
      )}
      {compliance.violations.length > 0 && (
        <ul className="mt-2 space-y-1">
          {compliance.violations.map((v, i) => (
            <li
              key={i}
              className="flex items-start gap-1.5 text-xs text-critical"
            >
              <span aria-hidden="true">⚠</span>
              <span>{v}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/**
 * Human-in-the-loop approval dialog. Renders the AI's reasoning, the proposed
 * staffing plan, and the compliance verdict, and lets the administrator approve
 * or dismiss. Acts as an accessible modal dialog (focus-trapped, Esc to close).
 */
export function ApprovalModal({
  result,
  approving,
  onApprove,
  onDismiss,
}: ApprovalModalProps) {
  const titleId = useId();
  const containerRef = useFocusTrap<HTMLDivElement>(true, onDismiss);

  const committed = result.committed;
  const canApprove = result.awaiting_approval && !approving;
  const complianceRejected = result.compliance?.status === "rejected";

  return (
    <div
      className="animate-fade fixed inset-0 z-50 flex items-end justify-center bg-ink/40 p-0 backdrop-blur-[2px] sm:items-center sm:p-6"
      onMouseDown={(e) => {
        // Dismiss when clicking the backdrop (but not the dialog itself).
        if (e.target === e.currentTarget) onDismiss();
      }}
    >
      <div
        ref={containerRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className="animate-rise flex max-h-[92vh] w-full max-w-lg flex-col overflow-hidden rounded-t-2xl border border-hairline bg-surface shadow-2xl outline-none sm:rounded-2xl"
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-3 border-b border-hairline px-5 py-4">
          <div>
            <p className="text-[0.7rem] font-semibold uppercase tracking-[0.14em] text-accent">
              {committed ? "Plan committed" : "Approval required"}
            </p>
            <h2 id={titleId} className="mt-0.5 text-lg font-semibold text-ink">
              Staff reallocation plan
            </h2>
          </div>
          <RiskBadge level={result.risk_level} />
        </div>

        {/* Scrollable body */}
        <div className="flex-1 space-y-4 overflow-y-auto px-5 py-4">
          {committed && (
            <div className="flex items-center gap-2 rounded-lg border border-calm/30 bg-calm/10 px-3 py-2.5 text-sm font-medium text-calm">
              <span aria-hidden="true">✓</span>
              This plan has been approved and committed.
            </div>
          )}

          {result.triage_assessment && (
            <Section title="Triage assessment">
              <p className="text-sm leading-relaxed text-ink/85">
                {result.triage_assessment}
              </p>
            </Section>
          )}

          {result.resource_recommendation && (
            <Section title="Resource recommendation">
              <p className="text-sm leading-relaxed text-ink/85">
                {result.resource_recommendation}
              </p>
            </Section>
          )}

          <Section title="Proposed changes">
            {result.plan ? (
              <>
                {result.plan.summary && (
                  <p className="mb-2 text-sm leading-relaxed text-ink/85">
                    {result.plan.summary}
                  </p>
                )}
                {result.plan.changes.length > 0 ? (
                  <ul className="rounded-lg border border-hairline px-3">
                    {result.plan.changes.map((change, i) => (
                      <PlanChangeRow key={i} change={change} />
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted">
                    No staffing changes proposed.
                  </p>
                )}
              </>
            ) : (
              <p className="rounded-lg border border-hairline bg-canvas px-3 py-3 text-sm text-muted">
                No reallocation plan was generated for this assessment.
              </p>
            )}
          </Section>

          {result.compliance && (
            <Section title="Compliance verdict">
              <CompliancePanel compliance={result.compliance} />
            </Section>
          )}
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-end gap-3 border-t border-hairline bg-canvas px-5 py-3">
          <button
            type="button"
            onClick={onDismiss}
            className="rounded-lg border border-hairline bg-surface px-4 py-2 text-sm font-semibold text-ink transition-colors hover:bg-canvas"
          >
            {committed ? "Close" : "Dismiss"}
          </button>
          {!committed && (
            <button
              type="button"
              onClick={() => onApprove(result.thread_id)}
              disabled={!canApprove}
              aria-busy={approving}
              className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-55"
            >
              {approving ? "Approving…" : "Approve plan"}
            </button>
          )}
        </div>

        {complianceRejected && !committed && (
          <p className="px-5 pb-3 text-center text-xs text-critical">
            Compliance flagged violations — review carefully before approving.
          </p>
        )}
      </div>
    </div>
  );
}
