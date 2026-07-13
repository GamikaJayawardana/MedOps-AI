import type { ConnectionStatus as Status } from "@/lib/types";

interface ConnectionStatusProps {
  status: Status;
}

const CONFIG: Record<
  Status,
  { label: string; dot: string; text: string; live: boolean }
> = {
  connecting: {
    label: "Connecting",
    dot: "bg-busy",
    text: "text-busy",
    live: true,
  },
  connected: {
    label: "Live",
    dot: "bg-calm",
    text: "text-calm",
    live: true,
  },
  closed: {
    label: "Reconnecting",
    dot: "bg-busy",
    text: "text-busy",
    live: true,
  },
  error: {
    label: "Connection error",
    dot: "bg-critical",
    text: "text-critical",
    live: false,
  },
};

/** Compact live/degraded indicator for the header. */
export function ConnectionStatus({ status }: ConnectionStatusProps) {
  const cfg = CONFIG[status];
  return (
    <div
      className="inline-flex items-center gap-2 rounded-full border border-hairline bg-surface px-3 py-1.5"
      role="status"
      aria-live="polite"
    >
      <span className="relative flex h-2.5 w-2.5">
        {cfg.live && (
          <span
            className={`absolute inline-flex h-full w-full rounded-full opacity-60 ${cfg.dot} animate-pulse-dot`}
            aria-hidden="true"
          />
        )}
        <span
          className={`relative inline-flex h-2.5 w-2.5 rounded-full ${cfg.dot}`}
        />
      </span>
      <span className={`text-xs font-semibold ${cfg.text}`}>{cfg.label}</span>
    </div>
  );
}
