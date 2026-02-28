"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bot,
  Brain,
  Search,
  Database,
  Cpu,
  GitBranch,
  LayoutDashboard,
  ShieldCheck,
  Activity,
} from "lucide-react";

type AgentItem = {
  name: string;
  description: string;
  icon: any;
  accent: string;
  details: string[];
};

type ViewState = "DS" | "LOM" | "ML";

const agentsData: Record<ViewState, AgentItem[]> = {
  DS: [
    {
      name: "Dataset Profiler (DPSU)",
      description:
        "Rapid column analysis, distribution detection, missing value assessment, and contextual domain inference.",
      icon: Search,
      accent: "#22D3EE",
      details: [
        "Infers semantic roles of columns",
        "Detects distributions and statistical anomalies",
        "Assesses severity of missing values",
        "Determines dataset's real-world business context",
      ],
    },
    {
      name: "Intent Inference (QBII)",
      description:
        "Interprets analytical goals from user inputs and metadata to map out downstream reasoning rules.",
      icon: Brain,
      accent: "#3B82F6",
      details: [
        "Clarifies high-level analytical objectives",
        "Maps user questions to statistical execution paths",
        "Enforces stakeholder-specific constraints",
        "Establishes analytical scope",
      ],
    },
    {
      name: "Hypothesis Engine (IHE)",
      description:
        "Generates real-world explanations for detected patterns and pauses for structural Human-In-The-Loop approval.",
      icon: GitBranch,
      accent: "#A855F7",
      details: [
        "Formulates statistically sound hypotheses",
        "Generates causal reasoning traces",
        "Gates progression via HITL validation",
        "Provides human-readable insights",
      ],
    },
    {
      name: "Data Integrity Layer",
      description:
        "Autonomously handles missing values, types, and outliers while explicitly recording repair justifications.",
      icon: Database,
      accent: "#22C55E",
      details: [
        "Removes duplicate records safely",
        "Corrects mismatched data types",
        "Imputes missing values with contextual reasoning",
        "Records all modifications to the Global Analysis Ledger",
      ],
    },
  ],
  LOM: [
    {
      name: "LOM Profiler",
      description:
        "Navigates and extracts key structural information and metadata elements from standardized IEEE LOM XML.",
      icon: Search,
      accent: "#FBBF24",
      details: [
        "Parses deep XML structures",
        "Extracts educational metadata and taxonomy",
        "Validates structural schema compliance",
        "Highlights missing core metadata fields",
      ],
    },
    {
      name: "Timeline Constructor",
      description:
        "Reads LOM histories to reconstruct temporal sequences of object lifecycle events and modifications.",
      icon: Activity,
      accent: "#F97316",
      details: [
        "Extracts timestamped modification events",
        "Reconstructs sequential lifecycle states",
        "Identifies temporal reporting gaps",
        "Maps versioning progressions",
      ],
    },
    {
      name: "Narrative Reporter (RG)",
      description:
        "Aggregates structural profile, lifecycle events, and root causes into a unified, human-readable compliance document.",
      icon: LayoutDashboard,
      accent: "#38BDF8",
      details: [
        "Generates final human-readable summaries",
        "Highlights technical interoperability issues",
        "Documents educational utility context",
        "References causal logic from the Ledger",
      ],
    },
  ],
  ML: [
    {
      name: "Problem Framer (PFTDC)",
      description:
        "Translates business objectives into concrete predictive modeling tasks and shapes the initial training data.",
      icon: Cpu,
      accent: "#F43F5E",
      details: [
        "Selects appropriate target variables",
        "Prepares algorithmic training splits",
        "Manages class imbalance strategies",
        "Formulates the core machine learning objective",
      ],
    },
    {
      name: "Candidate Generator",
      description:
        "Reasons over available algorithms to select interpretable and highly accurate model architectures.",
      icon: Bot,
      accent: "#8B5CF6",
      details: [
        "Matches algorithms to data profiles",
        "Prioritizes interpretable models by default",
        "Tunes hyperparameter sweeps autonomously",
        "Executes training evaluation comparisons",
      ],
    },
    {
      name: "Deployment Manager",
      description:
        "Enforces performance constraints, validates predictions against rules, and prepares final model payload.",
      icon: ShieldCheck,
      accent: "#EAB308",
      details: [
        "Validates model reliability and baseline fairness",
        "Creates specialized microservice payload artifacts",
        "Attaches data drift monitoring hooks",
        "Prepares isolated container instructions",
      ],
    },
  ],
};

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.1 },
  },
};

function AgentCard({ agent }: { agent: AgentItem }) {
  const [isHovering, setIsHovering] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isHovering && !isExpanded) {
      timeoutRef.current = setTimeout(() => {
        setIsExpanded(true);
      }, 1500);
    } else if (!isHovering) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      setIsExpanded(false);
    }

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [isHovering, isExpanded]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      onFocus={() => setIsHovering(true)}
      onBlur={() => setIsHovering(false)}
      className="group relative flex flex-col bg-[#0A0A0A] border border-white/[0.06] rounded-xl p-7 hover:border-white/[0.12] transition-colors duration-300 overflow-hidden outline-none"
      tabIndex={0}
    >
      {/* Accent top line */}
      <div
        className="absolute top-0 left-6 right-6 h-[1px] opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: `linear-gradient(90deg, transparent, ${agent.accent}, transparent)`,
        }}
      />

      <div
        className="w-10 h-10 flex items-center justify-center rounded-lg mb-5 transition-colors duration-300 shrink-0"
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
      <p className="text-sm text-white/40 leading-relaxed z-10">
        {agent.description}
      </p>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: "auto", marginTop: 16 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            className="border-t border-white/5 z-10"
          >
            <div className="pt-4 pb-2">
              <h4
                className="text-xs uppercase tracking-[0.15em] mb-4 font-semibold"
                style={{
                  color: agent.accent,
                  fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
                }}
              >
                Core Capabilities
              </h4>
              <ul className="space-y-3">
                {agent.details.map((detail, idx) => (
                  <motion.li
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 + idx * 0.05 }}
                    className="text-sm text-white/60 flex items-start"
                  >
                    <span
                      className="mr-3 opacity-50 block mt-1 shrink-0"
                      style={{ color: agent.accent }}
                    >
                      •
                    </span>
                    <span>{detail}</span>
                  </motion.li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hold-to-reveal Progress Bar Indicator */}
      <div className="absolute bottom-0 left-0 w-full h-[2px] bg-transparent overflow-hidden">
        <motion.div
          className="h-full"
          style={{ backgroundColor: agent.accent }}
          initial={{ width: "0%", opacity: 0 }}
          animate={{
            width: isExpanded ? "100%" : isHovering ? "100%" : "0%",
            opacity: isExpanded ? 0 : isHovering ? 0.7 : 0,
          }}
          transition={{
            duration: isHovering && !isExpanded ? 1.5 : 0.3,
            ease: isHovering && !isExpanded ? "linear" : "easeOut",
          }}
        />
      </div>

      {/* Soft background glow on expanded */}
      <motion.div
        className="absolute inset-0 z-0 pointer-events-none mix-blend-screen"
        initial={{ opacity: 0 }}
        animate={{ opacity: isExpanded ? 0.03 : 0 }}
        style={{
          background: `radial-gradient(circle at 100% 100%, ${agent.accent}, transparent 60%)`,
        }}
      />
    </motion.div>
  );
}

export function AgentShowcase() {
  const [activeTab, setActiveTab] = useState<ViewState>("DS");

  const tabs: { id: ViewState; label: string }[] = [
    { id: "DS", label: "Data Science" },
    { id: "LOM", label: "Object Metadata" },
    { id: "ML", label: "Machine Learning" },
  ];

  return (
    <section
      id="agents"
      className="relative py-24 lg:py-32 bg-black overflow-hidden"
    >
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <span
            className="inline-block text-xs tracking-[0.2em] text-[#F97316] mb-4 uppercase"
            style={{
              fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
            }}
          >
            Intelligence Core
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
            Domain-Specific{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#3B82F6] to-[#F97316]">
              Agents
            </span>
          </h2>
          <p className="text-base text-white/40 max-w-2xl mx-auto leading-relaxed mb-10">
            Explore the specialized reasoning agents that drive our pipelines.
            Hold your cursor over any agent to dive deep into its core
            capabilities.
          </p>

          {/* View Controls */}
          <div className="inline-flex bg-[#0A0A0A] border border-white/10 rounded-full p-1 self-center">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-6 py-2.5 text-sm font-medium transition-colors rounded-full ${
                  activeTab === tab.id
                    ? "text-white"
                    : "text-white/40 hover:text-white/70"
                }`}
                style={{
                  fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
                }}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="agentTabPill"
                    className="absolute inset-0 bg-white/10 rounded-full border border-white/20"
                    initial={false}
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                  />
                )}
                <span className="relative z-10 tracking-wide">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Cards Grid */}
        <motion.div
          className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6 min-h-[400px]"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
        >
          <AnimatePresence mode="popLayout">
            {agentsData[activeTab].map((agent, i) => (
              <AgentCard key={`${activeTab}-${agent.name}`} agent={agent} />
            ))}
          </AnimatePresence>
        </motion.div>
      </div>
    </section>
  );
}
