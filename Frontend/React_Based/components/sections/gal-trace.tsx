"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";

const traceSteps = [
    { agent: "REASONING", action: "Parsing user intent...", status: "ok", time: "0.12s" },
    { agent: "REASONING", action: "Detected objective: predict churn probability", status: "ok", time: "0.04s" },
    { agent: "PROFILER", action: "Scanning dataset → 14 columns, 10,842 rows", status: "ok", time: "0.31s" },
    { agent: "PROFILER", action: "Null analysis → 3 columns with > 5% missing", status: "warn", time: "0.08s" },
    { agent: "PIPELINE", action: "Initiating feature engineering pass", status: "ok", time: "0.22s" },
    { agent: "PIPELINE", action: "Encoding categorical: region, plan_type, channel", status: "ok", time: "0.45s" },
    { agent: "HITL_GATE", action: "Hypothesis: LogisticRegression baseline → Accept / Reject?", status: "gate", time: "—" },
    { agent: "PIPELINE", action: "User accepted → Training LogisticRegression", status: "ok", time: "2.14s" },
    { agent: "PIPELINE", action: "Cross-validation AUC: 0.847 ± 0.012", status: "ok", time: "1.87s" },
    { agent: "GOVERNANCE", action: "Audit log written → trace_id: gal_0x8f3a", status: "ok", time: "0.03s" },
];

function statusColor(status: string) {
    switch (status) {
        case "ok": return "#22C55E";
        case "warn": return "#EAB308";
        case "gate": return "#F97316";
        default: return "#6B7280";
    }
}

export function GalTrace() {
    const [visibleLines, setVisibleLines] = useState(0);
    const containerRef = useRef<HTMLDivElement>(null);
    const hasAnimated = useRef(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !hasAnimated.current) {
                    hasAnimated.current = true;
                    let i = 0;
                    const timer = setInterval(() => {
                        i++;
                        setVisibleLines(i);
                        if (i >= traceSteps.length) clearInterval(timer);
                    }, 350);
                }
            },
            { threshold: 0.3 }
        );

        if (containerRef.current) observer.observe(containerRef.current);
        return () => observer.disconnect();
    }, []);

    return (
        <section id="gal-trace" className="relative py-24 lg:py-32 bg-[#0A0A0A] overflow-hidden">
            {/* Top rule */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-16">
                    <span
                        className="inline-block text-xs tracking-[0.2em] text-[#F97316] mb-4 uppercase"
                        style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                    >
                        Transparency
                    </span>
                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
                        Global Analysis{" "}
                        <span className="text-[#F97316]">Ledger</span>
                    </h2>
                    <p className="text-base text-white/40 max-w-2xl mx-auto leading-relaxed">
                        Every reasoning step, every agent decision, every data transformation — traceable, auditable, and transparent.
                    </p>
                </div>

                {/* Trace Terminal */}
                <div ref={containerRef} className="max-w-4xl mx-auto">
                    <div className="relative rounded-xl border border-white/[0.06] bg-black overflow-hidden">
                        {/* Terminal title bar */}
                        <div className="flex items-center gap-2 px-4 py-3 border-b border-white/[0.06] bg-[#0A0A0A]">
                            <div className="flex gap-1.5">
                                <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                                <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                                <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                            </div>
                            <span
                                className="text-[10px] tracking-[0.15em] text-white/30 ml-3 uppercase"
                                style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                            >
                                GAL Reasoning Trace — Session 0x8f3a
                            </span>
                        </div>

                        {/* Trace lines */}
                        <div className="p-5 space-y-1 min-h-[320px]" style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}>
                            {traceSteps.map((step, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={i < visibleLines ? { opacity: 1, x: 0 } : {}}
                                    transition={{ duration: 0.3 }}
                                    className="flex items-start gap-3 text-xs leading-relaxed"
                                >
                                    {/* Status dot */}
                                    <span
                                        className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                                        style={{ backgroundColor: statusColor(step.status) }}
                                    />

                                    {/* Agent label */}
                                    <span
                                        className="w-24 shrink-0 text-white/30"
                                    >
                                        [{step.agent}]
                                    </span>

                                    {/* Action */}
                                    <span className="text-white/60 flex-1">
                                        {step.action}
                                    </span>

                                    {/* Time */}
                                    <span className="text-white/20 shrink-0 text-right w-14">
                                        {step.time}
                                    </span>
                                </motion.div>
                            ))}

                            {/* Typing cursor */}
                            {visibleLines >= traceSteps.length && (
                                <div className="flex items-center gap-2 pt-2">
                                    <span className="text-[#3B82F6] text-xs">▸</span>
                                    <span className="w-2 h-4 bg-[#3B82F6] animate-typing-cursor" />
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
