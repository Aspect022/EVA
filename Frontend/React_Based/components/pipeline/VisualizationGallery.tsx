"use client"

import { motion } from "framer-motion"
import { ChevronRight, BarChart3, AlertCircle } from "lucide-react"
import { PlotlyChart } from "@/components/PlotlyWrapper"

interface VisualizationEntry {
  question: string
  chart_type: string
  interpretation: string
  confidence_note: string
  validation_result: string
  plotly_config: Record<string, unknown> | null
  variables_used: string[]
  related_finding: string
  chart_type_reasoning: string
  audience_calibration: string
}

interface VisualizationGalleryProps {
  visualizations: VisualizationEntry[]
  totalRendered: number
  totalFailed: number
  overallReasoning: string
  onNext: () => void
}

const cardVariants = {
  hidden: { opacity: 0, y: 20, scale: 0.97 },
  visible: (i: number) => ({
    opacity: 1, y: 0, scale: 1,
    transition: { delay: i * 0.1, type: "spring" as const, stiffness: 80, damping: 16 },
  }),
}

export function VisualizationGallery({
  visualizations,
  totalRendered,
  totalFailed,
  overallReasoning,
  onNext,
}: VisualizationGalleryProps) {
  const rendered = visualizations.filter(v => v.validation_result === "passed" && v.plotly_config)
  const failed = visualizations.filter(v => v.validation_result !== "passed" || !v.plotly_config)

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
          <BarChart3 className="w-3.5 h-3.5" />
          VPE Results
        </div>
        <h2 className="text-2xl font-bold text-white">Visualization Gallery</h2>
        <p className="text-white/40 max-w-xl mx-auto text-sm">
          {totalRendered} chart{totalRendered !== 1 ? "s" : ""} rendered
          {totalFailed > 0 && <span className="text-amber-400"> • {totalFailed} failed</span>}
        </p>
        {overallReasoning && (
          <p className="text-white/30 text-xs max-w-2xl mx-auto italic">{overallReasoning}</p>
        )}
      </motion.div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {rendered.map((viz, i) => (
          <motion.div
            key={i}
            custom={i}
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            className="bg-[#0A0A0A] border border-white/[0.06] rounded-2xl overflow-hidden hover:border-white/[0.12] transition-colors"
          >
            {/* Chart */}
            <div className="p-4">
              {viz.plotly_config && (
                <PlotlyChart
                  data={((viz.plotly_config as Record<string, unknown>).data as unknown[]) || []}
                  layout={(viz.plotly_config as Record<string, unknown>).layout as Record<string, unknown>}
                />
              )}
            </div>

            {/* Info */}
            <div className="px-5 pb-5 space-y-2 border-t border-white/[0.04] pt-4">
              <h3 className="text-sm font-semibold text-white leading-snug">{viz.question}</h3>
              <p className="text-xs text-white/50 leading-relaxed">{viz.interpretation}</p>
              {viz.confidence_note && (
                <p className="text-xs text-amber-400/60 italic">{viz.confidence_note}</p>
              )}
              <div className="flex items-center gap-2 pt-1">
                <span className="px-2 py-0.5 rounded-md bg-white/[0.04] text-[10px] font-mono text-white/40 uppercase">
                  {viz.chart_type}
                </span>
                <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-[10px] font-mono text-emerald-400 uppercase">
                  passed
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Failed visualizations summary */}
      {failed.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 space-y-2"
        >
          <div className="flex items-center gap-2 text-amber-400 text-sm font-medium">
            <AlertCircle className="w-4 h-4" />
            {failed.length} visualization{failed.length !== 1 ? "s" : ""} could not be rendered
          </div>
          <div className="space-y-1">
            {failed.map((viz, i) => (
              <p key={i} className="text-xs text-white/40">• {viz.question}</p>
            ))}
          </div>
        </motion.div>
      )}

      {/* Next Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
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
