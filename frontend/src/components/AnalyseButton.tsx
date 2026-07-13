interface AnalyseButtonProps {
  onAnalyse: () => void;
  running: boolean;
  disabled?: boolean;
}

/** Small inline spinner; honours reduced-motion via the global CSS override. */
function Spinner() {
  return (
    <svg
      className="h-4 w-4 animate-spin"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="12"
        cy="12"
        r="9"
        stroke="currentColor"
        strokeWidth="3"
        opacity="0.25"
      />
      <path
        d="M21 12a9 9 0 0 0-9-9"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
}

/**
 * Triggers a manual multi-agent analysis. Shows a loading state from the moment
 * the request fires until the result arrives, and is disabled while offline.
 */
export function AnalyseButton({
  onAnalyse,
  running,
  disabled = false,
}: AnalyseButtonProps) {
  return (
    <button
      type="button"
      onClick={onAnalyse}
      disabled={running || disabled}
      aria-busy={running}
      className="inline-flex items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-accent/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-55"
    >
      {running ? (
        <>
          <Spinner />
          Analysing…
        </>
      ) : (
        <>
          <svg
            className="h-4 w-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M12 3v3m0 12v3M3 12h3m12 0h3M5.6 5.6l2.1 2.1m8.6 8.6 2.1 2.1m0-12.8-2.1 2.1m-8.6 8.6-2.1 2.1" />
            <circle cx="12" cy="12" r="3.5" />
          </svg>
          Analyse Now
        </>
      )}
    </button>
  );
}
