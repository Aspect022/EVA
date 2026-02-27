"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight } from "lucide-react"
import StarBorder from "@/components/star-border"
import { FloatingElement } from "@/components/motion-primitives"

const springTransition = {
  type: "spring" as const,
  stiffness: 80,
  damping: 18,
}

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.3,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 40, filter: "blur(6px)" },
  visible: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: springTransition,
  },
}

const headingWordVariants = {
  hidden: { opacity: 0, y: 30, rotateX: -40 },
  visible: {
    opacity: 1,
    y: 0,
    rotateX: 0,
    transition: { ...springTransition, stiffness: 60 },
  },
}

export function Hero() {
  const headingWords = ["AUTONOMOUS", "DATA", "SCIENCE."]

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-4 md:px-8 pt-20 pb-20 overflow-hidden">
      {/* Ambient Orbs — subtle depth, NOT mesh gradients */}
      <div className="absolute inset-0 pointer-events-none">
        <FloatingElement amplitude={15} duration={6} delay={0}>
          <div className="absolute top-20 left-10 w-80 h-80 bg-[var(--cta-orange)]/[0.03] rounded-full blur-3xl" />
        </FloatingElement>
        <FloatingElement amplitude={12} duration={7} delay={1}>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-cyan-400/[0.02] rounded-full blur-3xl" />
        </FloatingElement>
        <FloatingElement amplitude={8} duration={8} delay={2}>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[var(--dusk-blue)]/[0.02] rounded-full blur-3xl" />
        </FloatingElement>
      </div>

      {/* Decorative grid lines */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03]">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(249, 115, 22, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(249, 115, 22, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '80px 80px',
        }} />
      </div>

      <motion.div
        className="relative z-10 max-w-4xl text-center space-y-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Badge */}
        <motion.div
          variants={itemVariants}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card-premium cursor-default"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--cta-orange)] opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--cta-orange)]" />
          </span>
          <span className="text-xs font-mono text-[var(--dusty-denim)] uppercase tracking-wider">
            Now in Beta
          </span>
        </motion.div>

        {/* Heading with word-by-word reveal */}
        <div className="space-y-4">
          <h1 className="text-4xl md:text-7xl font-extrabold text-balance leading-tight perspective-[1000px]">
            <motion.span
              className="flex flex-wrap justify-center gap-x-4"
              variants={containerVariants}
            >
              {headingWords.map((word, i) => (
                <motion.span
                  key={word}
                  variants={headingWordVariants}
                  className="inline-block text-[var(--alabaster-grey)]"
                  style={{ transformOrigin: "center bottom" }}
                >
                  {word}
                </motion.span>
              ))}
            </motion.span>
            <br />
            <motion.span
              variants={itemVariants}
              className="inline-block animate-gradient-text text-4xl md:text-7xl font-extrabold mt-2"
            >
              LOCALIZED.
            </motion.span>
          </h1>

          <motion.p
            variants={itemVariants}
            className="text-lg md:text-2xl text-[var(--dusty-denim)] text-balance max-w-3xl mx-auto leading-relaxed"
          >
            Deploy powerful AI-driven analytics directly in your local
            environment. Full control, complete privacy, zero compromise.
          </motion.p>
        </div>

        {/* CTA Buttons */}
        <motion.div
          variants={itemVariants}
          className="flex flex-col sm:flex-row gap-4 justify-center pt-8"
        >
          <motion.div
            whileHover={{ scale: 1.04, y: -2 }}
            whileTap={{ scale: 0.97 }}
            transition={springTransition}
          >
            <Link href="/signup">
              <StarBorder color="#f97316" speed="6s">
                Get Started
                <ArrowRight className="w-5 h-5 ml-2 inline" />
              </StarBorder>
            </Link>
          </motion.div>
          <motion.div
            whileHover={{ scale: 1.04, y: -2 }}
            whileTap={{ scale: 0.97 }}
            transition={springTransition}
          >
            <Link
              href="#features"
              className="inline-flex items-center justify-center border border-[var(--dusk-blue)] text-[var(--alabaster-grey)] px-8 py-4 rounded-2xl text-base font-semibold hover:bg-[var(--prussian-blue)] hover:border-[var(--cta-orange)]/30 transition-all duration-300"
            >
              View Demo
            </Link>
          </motion.div>
        </motion.div>

        {/* Subtle scroll indicator */}
        <motion.div
          variants={itemVariants}
          className="pt-12"
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            className="mx-auto w-6 h-10 rounded-full border-2 border-[var(--dusk-blue)]/40 flex items-start justify-center p-1.5"
          >
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3], y: [0, 12, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              className="w-1.5 h-1.5 rounded-full bg-[var(--cta-orange)]"
            />
          </motion.div>
        </motion.div>
      </motion.div>
    </section>
  )
}
