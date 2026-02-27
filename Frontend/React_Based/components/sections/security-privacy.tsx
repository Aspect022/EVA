"use client";

import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDown, Server, ShieldCheck, Lock, FileCheck } from "lucide-react";
import { motion } from "framer-motion";

const items = [
    {
        id: "local",
        icon: Server,
        title: "100% Local Processing",
        content:
            "All computation runs on your hardware. No data leaves your machine — ever. EVA operates entirely within your local environment, using your CPU and GPU resources for model training and inference.",
    },
    {
        id: "no-cloud",
        icon: Lock,
        title: "Zero Cloud Dependency",
        content:
            "EVA requires no internet connection to operate. There are no external API calls, no telemetry, and no remote model endpoints. Your data stays under your complete control at all times.",
    },
    {
        id: "encryption",
        icon: ShieldCheck,
        title: "Session-Level Encryption",
        content:
            "Every EVA session generates a unique encryption context. Intermediate results, model artifacts, and trace logs are encrypted at rest using AES-256, keyed to your session identity.",
    },
    {
        id: "audit",
        icon: FileCheck,
        title: "Full Audit Trail",
        content:
            "The Global Analysis Ledger captures every reasoning step, agent decision, and data transformation. Complete provenance tracking ensures regulatory compliance and reproducibility.",
    },
];

export function SecurityPrivacy() {
    return (
        <section id="security" className="relative py-24 lg:py-32 bg-black overflow-hidden">
            {/* Top rule */}
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

            <div className="max-w-4xl mx-auto px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-16">
                    <span
                        className="inline-block text-xs tracking-[0.2em] text-[#22D3EE] mb-4 uppercase"
                        style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                    >
                        Trust
                    </span>
                    <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
                        Security &{" "}
                        <span className="text-[#22D3EE]">Privacy</span>
                    </h2>
                    <p className="text-base text-white/40 max-w-xl mx-auto leading-relaxed">
                        Built for enterprise-grade data governance. Your data never leaves your environment.
                    </p>
                </div>

                {/* Accordion */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-50px" }}
                    transition={{ duration: 0.6 }}
                >
                    <Accordion.Root type="single" collapsible className="space-y-3">
                        {items.map((item) => (
                            <Accordion.Item
                                key={item.id}
                                value={item.id}
                                className="group border border-white/[0.06] rounded-xl bg-[#0A0A0A] overflow-hidden data-[state=open]:border-white/[0.12] transition-colors duration-300"
                            >
                                <Accordion.Trigger className="flex items-center w-full px-6 py-5 text-left gap-4 cursor-pointer">
                                    <div className="w-9 h-9 flex items-center justify-center rounded-lg bg-white/[0.04] shrink-0">
                                        <item.icon className="w-4 h-4 text-[#22D3EE]" />
                                    </div>
                                    <span
                                        className="flex-1 text-sm font-medium text-white"
                                        style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                                    >
                                        {item.title}
                                    </span>
                                    <ChevronDown className="w-4 h-4 text-white/30 transition-transform duration-300 group-data-[state=open]:rotate-180" />
                                </Accordion.Trigger>
                                <Accordion.Content className="overflow-hidden data-[state=open]:animate-accordion-down data-[state=closed]:animate-accordion-up">
                                    <div className="px-6 pb-5 pt-0 pl-[76px]">
                                        <p className="text-sm text-white/40 leading-relaxed">{item.content}</p>
                                    </div>
                                </Accordion.Content>
                            </Accordion.Item>
                        ))}
                    </Accordion.Root>
                </motion.div>
            </div>
        </section>
    );
}
