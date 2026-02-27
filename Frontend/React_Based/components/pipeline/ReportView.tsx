"use client"

import { motion } from "framer-motion"
import { FileText, Quote, CheckCircle2 } from "lucide-react"

interface ReportViewProps {
  narrative: string
  citations: string[]
  communicatedRecommendations: string[]
  stakeholderCalibration: string
}

export function ReportView({
  narrative,
  citations,
  communicatedRecommendations,
  stakeholderCalibration,
}: ReportViewProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-4xl mx-auto mt-8 space-y-8 px-4 pb-8"
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-3"
      >
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0A0A0A] border border-white/[0.06] text-xs font-mono text-[#F97316] uppercase tracking-[0.15em]">
          <FileText className="w-3.5 h-3.5" />
          RG Report
        </div>
        <h2 className="text-2xl font-bold text-white">Analysis Report</h2>
        <p className="text-white/40 text-sm">
          Calibrated for: <span className="text-white/60">{stakeholderCalibration || "General"}</span>
        </p>
      </motion.div>

      {/* Narrative */}
      {narrative ? (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-[#0A0A0A] border border-white/[0.06] rounded-2xl p-8 space-y-4"
        >
          <div className="prose prose-invert prose-sm max-w-none">
            {narrative.split("\n").map((paragraph, i) => {
              if (!paragraph.trim()) return null
              if (paragraph.startsWith("#")) {
                const level = paragraph.match(/^#+/)?.[0].length || 1
                const text = paragraph.replace(/^#+\s*/, "")
                if (level === 1) return <h2 key={i} className="text-xl font-bold text-white mt-6 mb-3">{text}</h2>
                if (level === 2) return <h3 key={i} className="text-lg font-semibold text-white/90 mt-5 mb-2">{text}</h3>
                return <h4 key={i} className="text-base font-medium text-white/80 mt-4 mb-2">{text}</h4>
              }
              if (paragraph.startsWith("- ") || paragraph.startsWith("* ")) {
                return (
                  <div key={i} className="flex items-start gap-2 pl-2">
                    <span className="text-[#F97316] mt-1.5 text-xs">•</span>
                    <p className="text-sm text-white/70 leading-relaxed">{paragraph.slice(2)}</p>
                  </div>
                )
              }
              return <p key={i} className="text-sm text-white/70 leading-relaxed">{paragraph}</p>
            })}
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16 space-y-3"
        >
          <FileText className="w-12 h-12 text-white/20 mx-auto" />
          <p className="text-white/40">No report generated yet.</p>
        </motion.div>
      )}

      {/* Citations */}
      {citations.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-[#0A0A0A] border border-white/[0.06] rounded-xl p-5 space-y-3"
        >
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider flex items-center gap-2">
            <Quote className="w-4 h-4 text-blue-400" />
            Citations ({citations.length})
          </h3>
          <div className="space-y-1">
            {citations.map((citation, i) => (
              <p key={i} className="text-xs text-white/40 pl-4 border-l-2 border-white/[0.06] py-1">
                {citation}
              </p>
            ))}
          </div>
        </motion.div>
      )}

      {/* Communicated Recommendations */}
      {communicatedRecommendations.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35 }}
          className="bg-[#0A0A0A] border border-white/[0.06] rounded-xl p-5 space-y-3"
        >
          <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Communicated Recommendations ({communicatedRecommendations.length})
          </h3>
          <div className="space-y-1">
            {communicatedRecommendations.map((rec, i) => (
              <p key={i} className="text-xs text-white/50 flex items-start gap-2">
                <span className="text-emerald-400/60 mt-0.5">✓</span>
                {rec}
              </p>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
