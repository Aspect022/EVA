"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { ChevronUp, ChevronDown, Terminal, CheckCircle2, GripHorizontal } from "lucide-react"
import { useSession, PIPELINE_PHASES } from "@/lib/session-context"

export function GlobalAgenticLedger() {
  const [isExpanded, setIsExpanded] = useState(true)
  const [panelHeight, setPanelHeight] = useState(256)
  const { currentPhase, logs, isExecuting } = useSession()
  const logEndRef = useRef<HTMLDivElement>(null)
  const isDragging = useRef(false)
  const dragStartY = useRef(0)
  const dragStartHeight = useRef(0)

  const currentIdx = PIPELINE_PHASES.findIndex(p => p.id === currentPhase)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [logs.length])

  // Resize drag handlers
  const handleDragStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    isDragging.current = true
    dragStartY.current = e.clientY
    dragStartHeight.current = panelHeight

    const handleDragMove = (ev: MouseEvent) => {
      if (!isDragging.current) return
      const delta = dragStartY.current - ev.clientY
      setPanelHeight(Math.max(120, Math.min(600, dragStartHeight.current + delta)))
    }

    const handleDragEnd = () => {
      isDragging.current = false
      document.removeEventListener("mousemove", handleDragMove)
      document.removeEventListener("mouseup", handleDragEnd)
    }

    document.addEventListener("mousemove", handleDragMove)
    document.addEventListener("mouseup", handleDragEnd)
  }, [panelHeight])

  return (
    <div className="border-t border-[var(--dusk-blue)] bg-[var(--ink-black)] flex flex-col transition-all duration-300">
      {/* Resize Handle */}
      {isExpanded && (
        <div
          className="flex items-center justify-center py-1 cursor-row-resize hover:bg-[var(--prussian-blue)]/50 transition-colors group"
          onMouseDown={handleDragStart}
        >
          <GripHorizontal className="w-4 h-4 text-[var(--dusk-blue)] group-hover:text-[var(--dusty-denim)]" />
        </div>
      )}

      {/* Header / Tracker */}
      <div 
        className="flex items-center justify-between px-6 py-3 cursor-pointer hover:bg-[var(--prussian-blue)]/50 transition-colors border-b border-[var(--dusk-blue)]"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <Terminal className={`w-5 h-5 ${isExecuting ? "text-orange-400 animate-pulse" : "text-[var(--dusty-denim)]"}`} />
          <span className="font-semibold text-[var(--alabaster-grey)] tracking-wide">Global Agentic Ledger</span>
          {logs.length > 0 && (
            <span className="text-[10px] font-mono bg-[var(--prussian-blue)] border border-[var(--dusk-blue)] text-[var(--dusty-denim)] px-1.5 py-0.5 rounded">
              {logs.length}
            </span>
          )}
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
        <div 
          className="bg-[#050a10] overflow-y-auto p-4 font-mono text-sm custom-scrollbar"
          style={{ height: panelHeight }}
        >
          <ul className="space-y-1.5">
            {logs.length === 0 && (
              <li className="text-[var(--dusty-denim)] italic">Awaiting initialization...</li>
            )}
            
            {logs.map((log, idx) => (
              <li key={idx} className="flex items-start gap-3 hover:bg-[var(--prussian-blue)]/30 px-2 py-1 rounded transition-colors">
                <span className="text-[var(--dusty-denim)] opacity-60 shrink-0 select-none text-xs">[{log.timestamp}]</span>
                <span className={`font-bold w-12 shrink-0 truncate text-xs uppercase ${
                  log.type === "error" ? "text-red-400" :
                  log.type === "success" ? "text-green-400" :
                  "text-[var(--dusk-blue)]"
                }`}>{log.agent}</span>
                <span className={`break-words text-xs ${
                  log.type === "error" ? "text-red-400" :
                  log.type === "success" ? "text-green-400" :
                  log.type === "warn" ? "text-yellow-400" :
                  "text-[var(--alabaster-grey)]/80"
                }`}>
                  {log.message}
                </span>
              </li>
            ))}
          </ul>
          <div ref={logEndRef} />
        </div>
      )}
    </div>
  )
}
