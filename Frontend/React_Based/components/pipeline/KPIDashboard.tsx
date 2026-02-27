"use client"

import { motion } from "framer-motion"
import { ChevronRight, TrendingUp, AlertTriangle, Lightbulb, LayoutDashboard, Info } from "lucide-react"

interface KPI {
  name: string
  value: string | number
  justification: string
  derivation_source: string
}

interface DashboardAlert {
  alert_type: string
  description: string
  evidence_ref: string
  confidence: string
}

interface Recommendation {
  action: string
  target_group: string
  expected_impact: string
  urgency: string
  confidence: string
  supporting_evidence_ref: string
  supporting_hypothesis_ref: string
}

interface DashboardPanel {
  panel_name: string
  description: string
  elements: unknown[]
}

interface KPIDashboardProps {
  kpis: KPI[]
  alerts: DashboardAlert[]
  recommendations: Recommendation[]
  panels: DashboardPanel[]
  overallReasoning: string
  onNext: () => void
}

const alertTypeColors: Record<string, { bg: string; border: string; text: string; icon: string }> = {
  Critical: { bg: "bg-red-500/10", border: "border-red-500/30", text: "text-red-400", icon: "text-red-400" },
  Warning: { bg: "bg-amber-500/10", border: "border-amber-500/30", text: "text-amber-400", icon: "text-amber-400" },
  Info: { bg: "bg-blue-500/10", border: "border-blue-500/30", text: "text-blue-400", icon: "text-blue-400" },
}

const urgencyColors: Record<string, string> = {
  High: "text-red-400 bg-red-500/10 border-red-500/20",
  Medium: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  Low: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
}

export function KPIDashboard({
  kpis,
  alerts,
  recommendations,
  panels,
  overallReasoning,
  onNext,
}: KPIDashboardProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-6xl mx-auto mt-8 space-y-8 px-4 pb-8"
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-3"
      >
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0A0A0A] border border-white/[0.06] text-xs font-mono text-[#F97316] uppercase tracking-[0.15em]">
          <LayoutDashboard className="w-3.5 h-3.5" />
          ADC Results
        </div>
        <h2 className="text-2xl font-bold text-white">Analytical Dashboard</h2>
        <p className="text-white/40 text-sm">
          {kpis.length} KPIs • {alerts.length} Alerts • {recommendations.length} Recommendations
        </p>
        {overallReasoning && (
          <p className="text-white/30 text-xs max-w-2xl mx-auto italic">{overallReasoning}</p>
        )}
      </motion.div>

      {/* KPI Cards */}
      {kpis.length > 0 && (
        <section className="space-y-4">
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-[#F97316]" />
            Key Performance Indicators
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {kpis.map((kpi, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08, type: "spring", stiffness: 80 }}
                className="bg-[#0A0A0A] border border-white/[0.06] rounded-xl p-5 space-y-3 hover:border-[#F97316]/20 transition-colors"
              >
                <p className="text-xs font-mono text-white/40 uppercase tracking-wider">{kpi.name}</p>
                <p className="text-2xl font-bold text-white">{String(kpi.value) || "—"}</p>
                <p className="text-xs text-white/50 leading-relaxed">{kpi.justification}</p>
                {kpi.derivation_source && (
                  <p className="text-[10px] text-white/30 font-mono">Source: {kpi.derivation_source}</p>
                )}
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* Alerts */}
      {alerts.length > 0 && (
        <section className="space-y-4">
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Alerts
          </h3>
          <div className="space-y-3">
            {alerts.map((alert, i) => {
              const colors = alertTypeColors[alert.alert_type] || alertTypeColors.Info
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + i * 0.06 }}
                  className={`${colors.bg} ${colors.border} border rounded-xl p-4 space-y-2`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-semibold uppercase ${colors.text}`}>{alert.alert_type}</span>
                    <span className="text-[10px] text-white/30 font-mono">{alert.confidence} confidence</span>
                  </div>
                  <p className="text-sm text-white/80">{alert.description}</p>
                  {alert.evidence_ref && (
                    <p className="text-[10px] text-white/30 font-mono">Evidence: {alert.evidence_ref}</p>
                  )}
                </motion.div>
              )
            })}
          </div>
        </section>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <section className="space-y-4">
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-emerald-400" />
            Recommendations
          </h3>
          <div className="space-y-3">
            {recommendations.map((rec, i) => {
              const urgencyStyle = urgencyColors[rec.urgency] || urgencyColors.Medium
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + i * 0.06 }}
                  className="bg-[#0A0A0A] border border-white/[0.06] rounded-xl p-5 space-y-3 hover:border-emerald-500/20 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <p className="text-sm font-medium text-white">{rec.action}</p>
                    <span className={`shrink-0 px-2 py-0.5 rounded-md text-[10px] font-mono uppercase border ${urgencyStyle}`}>
                      {rec.urgency}
                    </span>
                  </div>
                  {rec.target_group && (
                    <p className="text-xs text-white/50">
                      <span className="text-white/30">Target:</span> {rec.target_group}
                    </p>
                  )}
                  {rec.expected_impact && (
                    <p className="text-xs text-white/50">
                      <span className="text-white/30">Expected Impact:</span> {rec.expected_impact}
                    </p>
                  )}
                  <div className="flex items-center gap-3 text-[10px] text-white/30 font-mono">
                    <span>{rec.confidence} confidence</span>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </section>
      )}

      {/* Panels Overview */}
      {panels.length > 0 && (
        <section className="space-y-4">
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider flex items-center gap-2">
            <Info className="w-4 h-4 text-blue-400" />
            Dashboard Panels
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {panels.map((panel, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + i * 0.06 }}
                className="bg-[#0A0A0A] border border-white/[0.06] rounded-xl p-4 space-y-2"
              >
                <p className="text-sm font-semibold text-white">{panel.panel_name}</p>
                <p className="text-xs text-white/50">{panel.description}</p>
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* Empty state */}
      {kpis.length === 0 && alerts.length === 0 && recommendations.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16 space-y-3"
        >
          <LayoutDashboard className="w-12 h-12 text-white/20 mx-auto" />
          <p className="text-white/40">No dashboard data available yet.</p>
        </motion.div>
      )}

      {/* Next Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="flex justify-center pt-4"
      >
        <motion.button
          whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(249, 115, 22, 0.2)" }}
          whileTap={{ scale: 0.97 }}
          onClick={onNext}
          className="inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-[#F97316] hover:bg-[#EA580C] text-white font-semibold transition-all cursor-pointer shadow-lg shadow-[#F97316]/20"
        >
          Next Step
          <ChevronRight className="w-5 h-5" />
        </motion.button>
      </motion.div>
    </motion.div>
  )
}
