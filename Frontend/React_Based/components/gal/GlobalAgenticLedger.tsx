"use client"

import { useState } from "react"
import { ChevronUp, ChevronDown, Terminal, CheckCircle2 } from "lucide-react"
import { useSession, PIPELINE_PHASES } from "@/lib/session-context"

export function GlobalAgenticLedger() {
  const [isExpanded, setIsExpanded] = useState(true)
  const { currentPhase, logs } = useSession()

  const currentIdx = PIPELINE_PHASES.findIndex(p => p.id === currentPhase)

  return (
    <div className="border-t border-[var(--dusk-blue)] bg-[var(--ink-black)] flex flex-col transition-all duration-300">
      <div 
        className="flex items-center justify-between px-6 py-3 cursor-pointer hover:bg-[var(--prussian-blue)]/50 transition-colors border-b border-[var(--dusk-blue)]"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <Terminal className="w-5 h-5 text-[var(--dusty-denim)]" />
          <span className="font-semibold text-[var(--alabaster-grey)] tracking-wide">Global Agentic Ledger</span>
        </div>
        
        <div className="hidden md:flex items-center gap-2 overflow-x-auto custom-scrollbar px-4 flex-1 justify-center">
          {PIPELINE_PHASES.slice(0, -1).map((phase, idx) => {
            const isCompleted = idx < currentIdx
            const isCurrent = idx === currentIdx
            return (
              <div key={phase.id} className="flex items-center gap-2">
                <div 
                  className={`flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold transition-all ${
                    isCompleted 
                      ? "bg-[var(--dusk-blue)]/30 text-[var(--alabaster-grey)] border border-[var(--dusk-blue)]" 
                      : isCurrent
                      ? "bg-[var(--alabaster-grey)] text-[var(--ink-black)]"
                      : "bg-[var(--prussian-blue)] text-[var(--dusty-denim)] border border-[var(--dusk-blue)]"
                  }`}
                  title={`${phase.agent}: ${phase.label}`}
                >
                  {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
                </div>
                
                {idx < PIPELINE_PHASES.length - 2 && (
                  <div className={`h-[1px] w-4 ${
                    isCompleted ? "bg-[var(--dusty-denim)]" : "bg-[var(--dusk-blue)]"
                  }`} />
                )}
              </div>
            )
          })}
        </div>

        <button className="p-1 rounded text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)]">
          {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
        </button>
      </div>

      {isExpanded && (
        <div className="h-48 md:h-56 bg-[#050a10] overflow-y-auto p-4 font-mono text-sm custom-scrollbar relative">
          <ul className="space-y-2">
            {logs.length === 0 && (
              <li className="text-[var(--dusty-denim)] italic">Awaiting initialization...</li>
            )}
            
            {logs.map((log, idx) => (
              <li key={idx} className="flex items-start gap-4 hover:bg-[var(--prussian-blue)]/30 px-2 py-1 rounded transition-colors">
                <span className="text-[var(--dusty-denim)] opacity-70 shrink-0 select-none">[{log.timestamp}]</span>
                <span className="text-[var(--dusk-blue)] font-bold w-16 shrink-0 truncate">{log.agent}</span>
                <span className={`break-words ${
                  log.type === "error" ? "text-red-400" :
                  log.type === "success" ? "text-green-400" :
                  log.type === "warn" ? "text-yellow-400" :
                  "text-[var(--alabaster-grey)]"
                }`}>
                  {log.message}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
