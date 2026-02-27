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
    <div className="border-t border-white/[0.06] bg-black flex flex-col transition-all duration-300">
      {/* Resize Handle */}
      {isExpanded && (
        <div
          className="flex items-center justify-center py-1 cursor-row-resize hover:bg-white/[0.04] transition-colors group"
          onMouseDown={handleDragStart}
        >
          <GripHorizontal className="w-4 h-4 text-white/20 group-hover:text-white/40" />
        </div>
      )}

      {/* Header / Tracker */}
      <div 
        className="flex items-center justify-between px-6 py-3 cursor-pointer hover:bg-white/[0.04] transition-colors border-b border-white/[0.06]"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <Terminal className={`w-5 h-5 ${isExecuting ? "text-orange-400 animate-pulse" : "text-white/40"}`} />
          <span className="font-semibold text-white tracking-wide">Global Agentic Ledger</span>
          {logs.length > 0 && (
            <span className="text-[10px] font-mono bg-[#0A0A0A] border border-white/[0.06] text-white/40 px-1.5 py-0.5 rounded">
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
                      ? "bg-[#3B82F6]/20 text-white border border-[#3B82F6]/30" 
                      : isCurrent
                      ? "bg-white text-black"
                      : "bg-[#0A0A0A] text-white/40 border border-white/[0.06]"
                  }`}
                  title={`${phase.agent}: ${phase.label}`}
                >
                  {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
                </div>
                
                {idx < PIPELINE_PHASES.length - 2 && (
                  <div className={`h-[1px] w-4 ${
                    isCompleted ? "bg-[#3B82F6]/40" : "bg-white/[0.06]"
                  }`} />
                )}
              </div>
            )
          })}
        </div>

        <button className="p-1 rounded text-white/40 hover:text-white">
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
              <li className="text-white/40 italic">Awaiting initialization...</li>
            )}
            
            {logs.map((log, idx) => (
              <li key={idx} className="flex items-start gap-3 hover:bg-white/[0.04] px-2 py-1 rounded transition-colors">
                <span className="text-white/20 opacity-60 shrink-0 select-none text-xs">[{log.timestamp}]</span>
                <span className={`font-bold w-12 shrink-0 truncate text-xs uppercase ${
                  log.type === "error" ? "text-red-400" :
                  log.type === "success" ? "text-green-400" :
                  "text-[#3B82F6]"
                }`}>{log.agent}</span>
                <span className={`break-words text-xs ${
                  log.type === "error" ? "text-red-400" :
                  log.type === "success" ? "text-green-400" :
                  log.type === "warn" ? "text-yellow-400" :
                  "text-white/60"
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
