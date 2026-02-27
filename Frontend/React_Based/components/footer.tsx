"use client"

import Link from "next/link"
import { motion, useInView } from "framer-motion"
import { useRef } from "react"

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { type: "spring" as const, stiffness: 80, damping: 16 },
  },
}

export function Footer() {
  const ref = useRef<HTMLElement>(null)
  const isInView = useInView(ref, { once: true, amount: 0.3 })

  return (
    <motion.footer
      id="footer"
      ref={ref}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      variants={containerVariants}
      className="relative bg-[var(--ink-black)] border-t border-[var(--dusk-blue)]/20 py-12 overflow-hidden"
    >
      {/* Subtle glow at top */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] h-[1px] bg-gradient-to-r from-transparent via-[var(--cta-orange)]/30 to-transparent" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <motion.div
          variants={itemVariants}
          className="flex flex-col md:flex-row items-center justify-between gap-6"
        >
          <div className="flex items-center gap-8">
            <Link href="/" className="text-[var(--alabaster-grey)] text-xl font-bold">
              <motion.span
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
                className="inline-block"
              >
                EVA
              </motion.span>
            </Link>
            <p className="text-sm text-[var(--dusty-denim)]">
              Autonomous Data Science. Localized.
            </p>
          </div>

          <div className="flex items-center gap-6">
            {["Privacy", "Terms", "Contact"].map((item) => (
              <motion.div
                key={item}
                whileHover={{ y: -2 }}
                transition={{ type: "spring", stiffness: 400, damping: 15 }}
              >
                <Link
                  href="#"
                  className="text-sm text-[var(--dusty-denim)] hover:text-[var(--cta-orange)] transition-colors duration-200 cursor-pointer"
                >
                  {item}
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div
          variants={itemVariants}
          className="mt-8 pt-8 border-t border-[var(--dusk-blue)]/20 text-center"
        >
          <p className="text-sm text-[var(--dusty-denim)]">
            © 2026 EVA. All rights reserved.
          </p>
        </motion.div>
      </div>
    </motion.footer>
  )
}
