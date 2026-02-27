"use client"

import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { Cpu, Lock, Zap, BarChart3, Database, Globe } from "lucide-react"

const features = [
  {
    icon: Cpu,
    title: "Autonomous AI Engine",
    description: "Self-learning algorithms that adapt to your data patterns without manual intervention.",
    accent: "from-orange-500/20 to-orange-600/5",
  },
  {
    icon: Lock,
    title: "Complete Privacy",
    description: "All processing happens locally. Your data never leaves your environment.",
    accent: "from-emerald-500/20 to-emerald-600/5",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Optimized for performance with GPU acceleration and parallel processing.",
    accent: "from-amber-500/20 to-amber-600/5",
  },
  {
    icon: BarChart3,
    title: "Advanced Analytics",
    description: "Deep insights with predictive modeling, anomaly detection, and trend analysis.",
    accent: "from-cyan-500/20 to-cyan-600/5",
  },
  {
    icon: Database,
    title: "Universal Data Support",
    description: "Connect to any data source — SQL, NoSQL, APIs, files, and streaming data.",
    accent: "from-rose-500/20 to-rose-600/5",
  },
  {
    icon: Globe,
    title: "Edge Deployment",
    description: "Deploy models at the edge for real-time inference with minimal latency.",
    accent: "from-teal-500/20 to-teal-600/5",
  },
]

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.12,
      delayChildren: 0.2,
    },
  },
}

const cardVariants = {
  hidden: { opacity: 0, y: 50, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: "spring" as const,
      stiffness: 80,
      damping: 16,
    },
  },
}

const headerVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring" as const,
      stiffness: 60,
      damping: 18,
    },
  },
}

export function Features() {
  const sectionRef = useRef<HTMLElement>(null)
  const isInView = useInView(sectionRef, { once: true, amount: 0.15 })

  return (
    <section
      id="features"
      ref={sectionRef}
      className="relative py-24 lg:py-32 bg-[var(--prussian-blue)] overflow-hidden"
    >
      {/* Background texture */}
      <div className="absolute inset-0 noise-overlay pointer-events-none" />

      {/* Subtle radial glow behind the grid */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[var(--cta-orange)]/[0.02] rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          variants={{
            hidden: {},
            visible: { transition: { staggerChildren: 0.15 } },
          }}
        >
          <motion.span
            variants={headerVariants}
            className="inline-block text-xs font-semibold uppercase tracking-[0.08em] text-[var(--cta-orange)] mb-4 font-mono animate-text-glow"
          >
            Features
          </motion.span>
          <motion.h2
            variants={headerVariants}
            className="text-3xl sm:text-4xl lg:text-5xl font-bold text-[var(--alabaster-grey)] mb-6 text-balance"
          >
            Everything you need for<br />autonomous data science
          </motion.h2>
          <motion.p
            variants={headerVariants}
            className="text-lg text-[var(--dusty-denim)] max-w-2xl mx-auto leading-relaxed"
          >
            Built for data scientists and engineers who demand control, privacy, and performance.
          </motion.p>
        </motion.div>

        {/* Feature cards grid */}
        <motion.div
          className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8"
          variants={containerVariants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
        >
          {features.map((feature) => (
            <motion.div
              key={feature.title}
              variants={cardVariants}
              whileHover={{
                y: -8,
                boxShadow: "0 20px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(249, 115, 22, 0.08)",
                borderColor: "rgba(249, 115, 22, 0.3)",
              }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
              className="group relative bg-[var(--ink-black)] border border-[var(--dusk-blue)]/30 rounded-2xl p-8 cursor-pointer overflow-hidden"
            >
              {/* Hover gradient overlay */}
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.accent} opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl`} />

              {/* Shimmer on hover */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 animate-shimmer rounded-2xl" />

              <div className="relative z-10">
                <motion.div
                  className="w-12 h-12 flex items-center justify-center rounded-xl bg-[var(--dusk-blue)]/20 mb-6 group-hover:bg-[var(--cta-orange)]/10 transition-all duration-300"
                  whileHover={{ rotate: [0, -10, 10, 0] }}
                  transition={{ duration: 0.5 }}
                >
                  <feature.icon className="w-6 h-6 text-[var(--dusty-denim)] group-hover:text-[var(--cta-orange)] transition-colors duration-300" />
                </motion.div>
                <h3 className="text-xl font-semibold text-[var(--alabaster-grey)] mb-3 group-hover:text-white transition-colors">
                  {feature.title}
                </h3>
                <p className="text-[var(--dusty-denim)] leading-relaxed group-hover:text-[var(--alabaster-grey)]/80 transition-colors">
                  {feature.description}
                </p>
              </div>

              {/* Corner accent line */}
              <div className="absolute bottom-0 left-0 w-0 h-[2px] bg-gradient-to-r from-[var(--cta-orange)] to-transparent group-hover:w-full transition-all duration-500" />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
