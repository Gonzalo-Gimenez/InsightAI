"use client";

import { useEffect, useState } from "react";

import { WorkspaceShell } from "@/components/workspace/workspace-shell";

export default function HomePage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div
        className="h-dvh bg-zinc-950"
        aria-busy="true"
        aria-label="Cargando workspace"
      />
    );
  }

  return <WorkspaceShell />;
}
