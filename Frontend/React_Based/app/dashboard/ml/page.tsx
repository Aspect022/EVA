"use client"

import { motion } from "framer-motion"

export default function MlComingSoonPage() {
  return (
    <div className="min-h-[calc(100vh-120px)] flex items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, y: 14, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ type: "spring", stiffness: 90, damping: 18 }}
        className="max-w-2xl w-full text-center bg-[#0A0A0A] border border-white/[0.06] rounded-2xl p-10 space-y-4"
      >
        <div className="text-[10px] font-mono uppercase tracking-[0.25em] text-white/40">
          Machine Learning
        </div>
        <h1 className="text-3xl font-black text-white tracking-tight">Coming soon…</h1>
        <p className="text-white/40">
          We’re building the ML workflow next (model training, evaluation, and deployment hooks).
        </p>
      </motion.div>
    </div>
  )
}

