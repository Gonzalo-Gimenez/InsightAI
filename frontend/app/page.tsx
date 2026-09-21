"use client";

import dynamic from "next/dynamic";

const WorkspaceShell = dynamic(
  () =>
    import("@/components/workspace/workspace-shell").then((mod) => ({
      default: mod.WorkspaceShell,
    })),
  {
    ssr: false,
    loading: () => (
      <div className="h-dvh bg-zinc-950" aria-busy="true" aria-label="Cargando workspace" />
    ),
  },
);

export default function HomePage() {
  return <WorkspaceShell />;
}
