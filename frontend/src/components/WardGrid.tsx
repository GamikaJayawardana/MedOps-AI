import type { WardTelemetry } from "@/lib/types";
import { WardCard } from "./WardCard";

interface WardGridProps {
  wards: WardTelemetry[];
  /** Number of ward slots to reserve before data arrives (avoids layout shift). */
  placeholderCount?: number;
}

/** Skeleton tile with the same footprint as a WardCard to reserve space. */
function WardCardSkeleton() {
  return (
    <div
      className="h-[164px] animate-pulse rounded-xl border border-hairline bg-surface"
      aria-hidden="true"
    />
  );
}

/**
 * Responsive ward grid: 1 column on mobile, 2 on tablet, 4 on desktop.
 * Renders same-sized skeletons before telemetry arrives so the layout is
 * stable from first paint (no CLS).
 */
export function WardGrid({ wards, placeholderCount = 4 }: WardGridProps) {
  const showSkeletons = wards.length === 0;

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {showSkeletons
        ? Array.from({ length: placeholderCount }, (_, i) => (
            <WardCardSkeleton key={i} />
          ))
        : wards.map((ward) => <WardCard key={ward.ward} ward={ward} />)}
    </div>
  );
}
