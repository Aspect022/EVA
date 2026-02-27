"use client"

import { motion } from "framer-motion"
import { Bot } from "lucide-react"
import { useSession, PIPELINE_PHASES } from "@/lib/session-context"

export function DashboardHeader() {
  const { currentPhase, isExecuting, getNextAgentName, rulesMode, setRulesMode } = useSession()
  const agentName = getNextAgentName()
  const phaseLabel = PIPELINE_PHASES.find(p => p.id === currentPhase)?.label ?? "—"

  return (
    <motion.header
      initial={{ y: -10, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
      className="h-16 border-b border-[var(--dusk-blue)]/30 bg-[var(--ink-black)]/90 backdrop-blur-md flex items-center justify-between px-8 shrink-0"
    >
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-[var(--alabaster-grey)]">Pipeline Dashboard</h1>
        <motion.span
          key={phaseLabel}
          initial={{ opacity: 0, scale: 0.8, y: -4 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ type: "spring", stiffness: 200, damping: 15 }}
          className="text-xs font-mono text-[var(--dusty-denim)] bg-[var(--prussian-blue)] px-2.5 py-1 rounded-lg border border-[var(--dusk-blue)]/30"
        >
          {phaseLabel}
        </motion.span>
      </div>

      <div className="flex items-center gap-4">
        {/* Rules Mode Toggle */}
        <div className="flex items-center bg-[var(--prussian-blue)] border border-[var(--dusk-blue)]/30 rounded-xl overflow-hidden">
          {(["lite", "full"] as const).map((mode) => (
            <motion.button
              key={mode}
              onClick={() => setRulesMode(mode)}
              whileHover={{ backgroundColor: "rgba(65, 90, 119, 0.3)" }}
              whileTap={{ scale: 0.95 }}
              className={`px-3 py-1.5 text-xs font-mono transition-all duration-200 cursor-pointer ${
                rulesMode === mode
                  ? "bg-[var(--dusk-blue)]/40 text-[var(--alabaster-grey)]"
                  : "text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)]"
              }`}
            >
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </motion.button>
          ))}
        </div>

        {/* Active Agent Widget */}
        <motion.div
          layout
          className="flex items-center gap-3 glass-card-premium px-4 py-2"
        >
          <motion.div
            animate={isExecuting ? { scale: [1, 1.1, 1] } : {}}
            transition={isExecuting ? { duration: 1.5, repeat: Infinity } : {}}
            className={`flex items-center justify-center w-8 h-8 rounded-lg border ${
              isExecuting
                ? "bg-orange-900/30 border-orange-500/30"
                : "bg-[var(--prussian-blue)] border-[var(--dusk-blue)]/30"
            }`}
          >
            <Bot
              className={`w-5 h-5 ${
                isExecuting ? "text-orange-400" : "text-[var(--dusty-denim)]"
              }`}
            />
          </motion.div>
          <div className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-[var(--dusty-denim)] font-mono">
              Active Agent
            </span>
            <motion.span
              key={agentName}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ type: "spring", stiffness: 200, damping: 15 }}
              className="text-sm font-bold text-[var(--alabaster-grey)]"
            >
              {agentName}
            </motion.span>
          </div>
        </motion.div>
      </div>
    </motion.header>
  )
}
