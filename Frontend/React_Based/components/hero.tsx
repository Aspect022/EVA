"use client"

import Link from "next/link"
import { ArrowRight } from "lucide-react"
import StarBorder from "@/components/star-border"

export function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-4 md:px-8 pt-20 pb-20 overflow-hidden">
      {/* Layer 2: Blur Orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-20 left-10 w-96 h-96 bg-cyan-400/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-400/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-4xl text-center space-y-8">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card glass-card-hover cursor-default">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400"></span>
          </span>
        </div>

        {/* Heading */}
        <div className="space-y-4">
          <h1 className="text-4xl md:text-7xl font-extrabold text-balance leading-tight">
            <span className="text-[var(--alabaster-grey)]">
              AUTONOMOUS{" "}
            </span>
            <span className="text-[var(--alabaster-grey)]">
              DATA SCIENCE.
            </span>
            <br />
            <span className="bg-gradient-to-r from-cyan-400 to-cyan-500 bg-clip-text text-transparent">
              LOCALIZED.
            </span>
          </h1>
          <p className="text-lg md:text-2xl text-[var(--dusty-denim)] text-balance max-w-3xl mx-auto leading-relaxed">
            Deploy powerful AI-driven analytics directly in your local
            environment. Full control, complete privacy, zero compromise.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
          <Link href="/signup">
            <StarBorder color="#00d4ff" speed="6s">
              Get Started
              <ArrowRight className="w-5 h-5 ml-2 inline" />
            </StarBorder>
          </Link>
          <Link
            href="#features"
            className="inline-flex items-center justify-center border border-[var(--dusk-blue)] text-[var(--alabaster-grey)] px-8 py-4 rounded-[20px] text-base font-semibold hover:bg-[var(--prussian-blue)] transition-colors"
          >
            View Demo
          </Link>
        </div>
      </div>
    </section>
  )
}
