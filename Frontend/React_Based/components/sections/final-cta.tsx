"use client";

import { motion } from "framer-motion";
import { Upload } from "lucide-react";

export function FinalCta() {
    return (
        <section id="cta" className="relative py-28 lg:py-36 bg-[#0A0A0A] overflow-hidden">
            {/* Top rule */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

            {/* Ambient glow */}
            <div className="absolute inset-0 pointer-events-none">
                <div
                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full opacity-30"
                    style={{
                        background: "radial-gradient(circle, rgba(59,130,246,0.12) 0%, rgba(249,115,22,0.06) 50%, transparent 70%)",
                    }}
                />
            </div>

            <div className="relative z-10 max-w-3xl mx-auto px-6 lg:px-8 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-50px" }}
                    transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
                >
                    <span
                        className="inline-block text-xs tracking-[0.2em] text-[#F97316] mb-4 uppercase"
                        style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                    >
                        Get Started
                    </span>

                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
                        Upload your data.
                        <br />
                        <span className="text-[#3B82F6]">Let EVA reason.</span>
                    </h2>

                    <p className="text-base text-white/40 max-w-lg mx-auto mb-10 leading-relaxed">
                        Drop a CSV, connect a database, or point to an API. EVA builds the pipeline,
                        runs the analysis, and delivers interpretable results — autonomously.
                    </p>

                    <button
                        className="inline-flex items-center gap-3 px-8 py-4 rounded-full text-white font-semibold text-base tracking-wide transition-all duration-300 hover:brightness-110 hover:scale-[1.02] active:scale-[0.98]"
                        style={{
                            background: "linear-gradient(135deg, #F97316, #EA580C)",
                            boxShadow: "0 0 40px rgba(249, 115, 22, 0.25)",
                        }}
                    >
                        <Upload className="w-5 h-5" />
                        START SESSION
                    </button>

                    <p
                        className="mt-6 text-xs text-white/20 tracking-wider"
                        style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                    >
                        No cloud. No signup. Runs locally.
                    </p>
                </motion.div>
            </div>
        </section>
    );
}
