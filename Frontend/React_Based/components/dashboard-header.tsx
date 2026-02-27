"use client"

import { Bot } from "lucide-react"
import { useSession, PIPELINE_PHASES } from "@/lib/session-context"

export function DashboardHeader() {
  const { currentPhase, isExecuting, getNextAgentName, rulesMode, setRulesMode } = useSession()
  const agentName = getNextAgentName()
  const phaseLabel = PIPELINE_PHASES.find(p => p.id === currentPhase)?.label ?? "—"

  return (
    <header className="h-16 border-b border-[var(--dusk-blue)] bg-[var(--ink-black)] flex items-center justify-between px-8 shrink-0">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-[var(--alabaster-grey)]">Pipeline Dashboard</h1>
        <span className="text-xs font-mono text-[var(--dusty-denim)] bg-[var(--prussian-blue)] px-2 py-1 rounded">{phaseLabel}</span>
      </div>
      
      <div className="flex items-center gap-4">
        {/* Rules Mode Toggle */}
        <div className="flex items-center bg-[var(--prussian-blue)] border border-[var(--dusk-blue)] rounded-lg overflow-hidden">
          <button
            onClick={() => setRulesMode("lite")}
            className={`px-3 py-1.5 text-xs font-mono transition-colors ${
              rulesMode === "lite"
                ? "bg-[var(--dusk-blue)] text-[var(--alabaster-grey)]"
                : "text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)]"
            }`}
          >
            Lite
          </button>
          <button
            onClick={() => setRulesMode("full")}
            className={`px-3 py-1.5 text-xs font-mono transition-colors ${
              rulesMode === "full"
                ? "bg-[var(--dusk-blue)] text-[var(--alabaster-grey)]"
                : "text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)]"
            }`}
          >
            Full
          </button>
        </div>

        {/* Active Agent Widget */}
        <div className="flex items-center gap-3 bg-[var(--prussian-blue)] border border-[var(--dusk-blue)] rounded-lg px-4 py-2">
          <div className={`flex items-center justify-center w-8 h-8 rounded-md border border-[var(--dusk-blue)] ${isExecuting ? "bg-orange-900/30 border-orange-500/30" : "bg-[var(--prussian-blue)]"}`}>
            <Bot className={`w-5 h-5 ${isExecuting ? "text-orange-400 animate-pulse" : "text-[var(--dusty-denim)]"}`} />
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-[var(--dusty-denim)] font-mono">Active Agent</span>
            <span className="text-sm font-bold text-[var(--alabaster-grey)]">{agentName}</span>
          </div>
        </div>
      </div>
    </header>
  )
}
