import { Dashboard } from "@/components/Dashboard";

/**
 * Route entry. The page shell stays a Server Component; all live/interactive
 * behaviour lives inside the <Dashboard> Client Component.
 */
export default function Home() {
  return (
    <main className="flex min-h-dvh flex-col bg-canvas">
      <Dashboard />
    </main>
  );
}
