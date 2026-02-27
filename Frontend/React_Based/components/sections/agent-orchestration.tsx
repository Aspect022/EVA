"use client";

import { motion } from "framer-motion";
import { Bot, Brain, Workflow, Cpu, GitBranch, Shield } from "lucide-react";

const agents = [
    {
        icon: Brain,
        name: "Reasoning Core",
        description: "Interprets user intent, selects strategy, and orchestrates sub-agents across the pipeline.",
        accent: "#3B82F6",
    },
    {
        icon: Workflow,
        name: "Pipeline Agent",
        description: "Executes multi-step ML workflows — feature engineering, model selection, hyperparameter tuning.",
        accent: "#F97316",
    },
    {
        icon: Bot,
        name: "Data Profiler",
        description: "Rapid column analysis, distribution detection, missing value assessment, and type inference.",
        accent: "#22D3EE",
    },
    {
        icon: Cpu,
        name: "Compute Allocator",
        description: "Manages local GPU/CPU resources for parallel execution and model training jobs.",
        accent: "#22C55E",
    },
    {
        icon: GitBranch,
        name: "Hypothesis Engine",
        description: "Generates statistical hypotheses, tests them against the data, and delivers interpretable results.",
        accent: "#A855F7",
    },
    {
        icon: Shield,
        name: "Governance Agent",
        description: "Enforces data access policies, audit logging, and HITL gating before production deployment.",
        accent: "#EAB308",
    },
];

const containerVariants = {
    hidden: {},
    visible: {
        transition: { staggerChildren: 0.1 },
    },
};

const cardVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] } },
};

export function AgentOrchestration() {
    return (
        <section id="agents" className="relative py-24 lg:py-32 bg-black overflow-hidden">
            {/* Subtle top gradient */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

            <div className="max-w-7xl mx-auto px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-16">
                    <span
                        className="inline-block text-xs tracking-[0.2em] text-[#3B82F6] mb-4 uppercase"
                        style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                    >
                        Architecture
                    </span>
                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
                        Multi-Agent{" "}
                        <span className="text-[#3B82F6]">Orchestration</span>
                    </h2>
                    <p className="text-base text-white/40 max-w-2xl mx-auto leading-relaxed">
                        EVA coordinates a fleet of specialized agents, each responsible for a distinct phase of the analytical pipeline —
                        from data ingestion to production deployment.
                    </p>
                </div>

                {/* Cards Grid */}
                <motion.div
                    className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6"
                    variants={containerVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, margin: "-50px" }}
                >
                    {agents.map((agent) => (
                        <motion.div
                            key={agent.name}
                            variants={cardVariants}
                            className="group relative bg-[#0A0A0A] border border-white/[0.06] rounded-xl p-7 hover:border-white/[0.12] transition-all duration-300"
                        >
                            {/* Accent top line */}
                            <div
                                className="absolute top-0 left-6 right-6 h-[1px] opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                                style={{ background: `linear-gradient(90deg, transparent, ${agent.accent}, transparent)` }}
                            />

                            <div
                                className="w-10 h-10 flex items-center justify-center rounded-lg mb-5 transition-colors duration-300"
                                style={{ backgroundColor: `${agent.accent}15` }}
                            >
                                <agent.icon
                                    className="w-5 h-5 transition-colors duration-300"
                                    style={{ color: agent.accent }}
                                />
                            </div>

                            <h3
                                className="text-base font-semibold text-white mb-2"
                                style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                            >
                                {agent.name}
                            </h3>
                            <p className="text-sm text-white/40 leading-relaxed">
                                {agent.description}
                            </p>
                        </motion.div>
                    ))}
                </motion.div>
            </div>
        </section>
    );
}
