"use client"

import Link from "next/link"
import Image from "next/image"
import { motion, useInView } from "framer-motion"
import { useRef } from "react"
import { Github, Twitter, Linkedin } from "lucide-react"

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

const linkGroups = [
  {
    title: "Product",
    links: [
      { label: "Documentation", href: "#" },
      { label: "Architecture", href: "#agents" },
      { label: "GAL Trace", href: "#gal-trace" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Privacy Policy", href: "#" },
      { label: "Terms of Service", href: "#" },
      { label: "Security", href: "#security" },
    ],
  },
];

const socials = [
  { icon: Github, href: "#", label: "GitHub" },
  { icon: Twitter, href: "#", label: "X / Twitter" },
  { icon: Linkedin, href: "#", label: "LinkedIn" },
];

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
      className="relative bg-[var(--ink-black)] border-t border-[var(--dusk-blue)]/20 py-16 overflow-hidden"
    >
      {/* Subtle glow at top */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[400px] h-[1px] bg-gradient-to-r from-transparent via-[var(--cta-orange)]/30 to-transparent" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 md:gap-8 mb-12">
          {/* Brand Column */}
          <motion.div variants={itemVariants} className="md:col-span-2">
            <Link href="/" className="inline-block mb-4">
              <motion.div
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
              >
                <Image
                  src="/logo.png"
                  alt="EVA"
                  width={80}
                  height={36}
                  className="h-[30px] w-auto object-contain brightness-0 invert"
                />
              </motion.div>
            </Link>
            <p className="text-sm text-[var(--dusty-denim)] max-w-xs leading-relaxed mb-6">
              Autonomous Data Science OS. Session-based analytical reasoning, multi-agent ML pipelines, and
              human-in-the-loop control — running entirely on your hardware.
            </p>

            {/* Social Icons */}
            <div className="flex items-center gap-3">
              {socials.map((social) => (
                <Link
                  key={social.label}
                  href={social.href}
                  aria-label={social.label}
                  className="w-8 h-8 flex items-center justify-center rounded-lg bg-[var(--dusk-blue)]/10 hover:bg-[var(--cta-orange)]/20 transition-colors"
                >
                  <social.icon className="w-4 h-4 text-[var(--dusty-denim)] hover:text-[var(--cta-orange)] transition-colors" />
                </Link>
              ))}
            </div>
          </motion.div>

          {/* Link Columns */}
          {linkGroups.map((group) => (
            <motion.div variants={itemVariants} key={group.title}>
              <h4
                className="text-xs tracking-[0.15em] text-[var(--alabaster-grey)]/50 uppercase mb-4"
                style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
              >
                {group.title}
              </h4>
              <ul className="space-y-3">
                {group.links.map((link) => (
                  <motion.li 
                    key={link.label}
                    whileHover={{ x: 2 }}
                    transition={{ type: "spring", stiffness: 400, damping: 15 }}
                  >
                    <Link
                      href={link.href}
                      className="text-sm text-[var(--dusty-denim)] hover:text-[var(--cta-orange)] transition-colors"
                    >
                      {link.label}
                    </Link>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Bottom bar */}
        <motion.div 
          variants={itemVariants}
          className="pt-8 border-t border-[var(--dusk-blue)]/20 flex flex-col sm:flex-row items-center justify-between gap-4"
        >
          <p
            className="text-xs text-[var(--dusty-denim)]"
            style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
          >
            © {new Date().getFullYear()} EVA. All rights reserved.
          </p>
          <p
            className="text-xs text-[var(--dusty-denim)]"
            style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
          >
            Built with autonomous intelligence.
          </p>
        </motion.div>
      </div>
    </motion.footer>
  );
}
