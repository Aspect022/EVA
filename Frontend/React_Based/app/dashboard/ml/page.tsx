"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useSession } from "@/lib/session-context";
import { MLResultsView } from "@/components/pipeline/MLResultsView";
import { GlobalAgenticLedger } from "@/components/gal/GlobalAgenticLedger";
import { useRouter } from "next/navigation";
import { ChevronLeft, Play } from "lucide-react";

const phaseTransition = {
  initial: { opacity: 0, y: 24, scale: 0.97, filter: "blur(4px)" },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    filter: "blur(0px)",
    transition: {
      type: "spring" as const,
      stiffness: 80,
      damping: 18,
      duration: 0.5,
    },
  },
  exit: {
    opacity: 0,
    y: -16,
    scale: 0.98,
    filter: "blur(2px)",
    transition: { duration: 0.25, ease: "easeInOut" as const },
  },
};

export default function MlPage() {
  const { mlDetails, isExecuting, runMLRL, sessionId } = useSession();
  const router = useRouter();

  const mlPhase: "ready" | "results" = mlDetails ? "results" : "ready";

  const renderContent = () => {
    if (!sessionId) {
      return (
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <p className="text-white/40">
            No active session found. Please start an analysis from the
            dashboard.
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            className="px-6 py-3 bg-white/10 hover:bg-white/15 border border-white/10 rounded-xl transition-colors font-medium text-white"
          >
            Go to Dashboard
          </button>
        </div>
      );
    }

    if (mlPhase === "results" && mlDetails) {
      return (
        <MLResultsView
          mlDetails={mlDetails}
          onNext={() => router.push("/dashboard")}
        />
      );
    }

    return (
      <PhaseAction
        title="Model Training & Evaluation"
        description="The ML Engine will build, train, and comprehensively evaluate predictive models (Random Forest, Gradient Boosting, SVM, etc.) to map out the strongest predictors of your target dimension."
        agentLabel="ML ENGINE"
        isExecuting={isExecuting}
        onRun={runMLRL}
      />
    );
  };

  return (
    <div className="h-full flex flex-col relative">
      <div className="flex-1 overflow-y-auto pb-72 px-6 pt-8">
        <button
          onClick={() => router.push("/dashboard")}
          className="mb-8 inline-flex items-center text-white/40 hover:text-white transition-colors"
        >
          <ChevronLeft className="w-4 h-4 mr-2" />
          Back to Data Science Pipeline
        </button>

        <AnimatePresence mode="wait">
          <motion.div key={mlPhase} {...phaseTransition}>
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="absolute bottom-0 left-0 right-0 z-50">
        <GlobalAgenticLedger />
      </div>
    </div>
  );
}

function PhaseAction({
  title,
  description,
  agentLabel,
  isExecuting,
  onRun,
}: {
  title: string;
  description: string;
  agentLabel: string;
  isExecuting: boolean;
  onRun: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 80, damping: 16 }}
      className="max-w-3xl mx-auto mt-16 text-center space-y-6"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
        className="inline-block px-3 py-1.5 rounded-lg bg-[#0A0A0A] border border-white/[0.06] text-xs font-mono text-[#F97316] uppercase tracking-[0.15em]"
        style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
      >
        {agentLabel}
      </motion.div>

      <motion.h2
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, type: "spring", stiffness: 80 }}
        className="text-4xl font-bold text-white tracking-tight"
      >
        {title}
      </motion.h2>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25 }}
        className="text-white/40 max-w-xl mx-auto text-lg leading-relaxed"
      >
        {description}
      </motion.p>

      <motion.button
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35, type: "spring", stiffness: 100 }}
        whileHover={{
          scale: 1.05,
          boxShadow: "0 0 30px rgba(249, 115, 22, 0.2)",
        }}
        whileTap={{ scale: 0.97 }}
        onClick={onRun}
        disabled={isExecuting}
        className="inline-flex items-center gap-3 px-8 py-4 mt-4 rounded-xl bg-[#F97316] hover:bg-[#EA580C] text-white font-semibold transition-all shadow-lg shadow-[#F97316]/20 disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
      >
        {isExecuting ? (
          <>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
            />
            Executing...
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            Run ML Pipeline
          </>
        )}
      </motion.button>
    </motion.div>
  );
}
