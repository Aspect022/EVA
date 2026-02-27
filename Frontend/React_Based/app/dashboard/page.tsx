"use client"

import { motion, AnimatePresence } from "framer-motion"
import { useSession } from "@/lib/session-context"
import { DatasetUpload } from "@/components/pipeline/DatasetUpload"
import { QuestionBuilder } from "@/components/pipeline/QuestionBuilder"
import { GlobalAgenticLedger } from "@/components/gal/GlobalAgenticLedger"
import { Play, CheckCircle2 } from "lucide-react"

const phaseTransition = {
  initial: { opacity: 0, y: 24, scale: 0.97, filter: "blur(4px)" },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    filter: "blur(0px)",
    transition: { type: "spring" as const, stiffness: 80, damping: 18, duration: 0.5 },
  },
  exit: {
    opacity: 0,
    y: -16,
    scale: 0.98,
    filter: "blur(2px)",
    transition: { duration: 0.25, ease: "easeInOut" as const },
  },
}

export default function DashboardPage() {
  const {
    currentPhase,
    isExecuting,
    questions,
    hypotheses,
    features,
    dashboardStats,
    report,
    quickModeEnabled,
    runPhase1a,
    submitUserAnswers,
    runPhase1b,
    runPhase2,
    runFIE,
    runVPE,
    runADC,
    runRG,
    runQuickMode,
  } = useSession()

  const renderPhaseContent = () => {
    switch (currentPhase) {
      case "upload":
        return <DatasetUpload />

      case "phase1a":
        return (
          <PhaseAction
            title={quickModeEnabled ? "Quick Mode — Full Pipeline" : "Profile & Generate Questions"}
            description={quickModeEnabled
              ? "All agents will simulate execution using cached analysis. This takes about 60–90 seconds."
              : "DPSU will profile your dataset and QBII will generate targeted questions."}
            agentLabel={quickModeEnabled ? "ALL AGENTS" : "DPSU + QBII"}
            isExecuting={isExecuting}
            onRun={quickModeEnabled ? runQuickMode : runPhase1a}
          />
        )

      case "answers":
        return questions.length > 0 ? (
          <QuestionBuilder
            questions={questions.map(q => ({
              question: (q as Record<string, string>).question || "",
              question_type: (q as Record<string, string>).question_type || "goal",
              why_asked: (q as Record<string, string>).why_asked || "",
            }))}
            onSubmit={(answers) => submitUserAnswers(answers)}
          />
        ) : (
          <LoadingState message="Waiting for questions from QBII..." />
        )

      case "phase1b":
        return (
          <PhaseAction
            title="Repair & Explore"
            description="DRIL will repair data integrity issues. EPR will run exploratory analysis."
            agentLabel="DRIL + EPR"
            isExecuting={isExecuting}
            onRun={runPhase1b}
          />
        )

      case "phase2":
        return (
          <PhaseAction
            title="Hypothesis Generation"
            description="IHE will generate analytical hypotheses from exploratory findings."
            agentLabel="IHE"
            isExecuting={isExecuting}
            onRun={runPhase2}
          />
        )

      case "fie":
        return (
          <PhaseAction
            title="Feature Intelligence"
            description="FIE will engineer features using domain knowledge from RAG."
            agentLabel="FIE"
            isExecuting={isExecuting}
            onRun={runFIE}
          />
        )

      case "vpe":
        return (
          <PhaseAction
            title="Visualization Planning"
            description="VPE will plan and generate charts from your data findings."
            agentLabel="VPE"
            isExecuting={isExecuting}
            onRun={runVPE}
          />
        )

      case "adc":
        return (
          <PhaseAction
            title="Analytical Dashboard"
            description="ADC will compose a dashboard with KPIs, alerts, and recommendations."
            agentLabel="ADC"
            isExecuting={isExecuting}
            onRun={runADC}
          />
        )

      case "rg":
        return (
          <PhaseAction
            title="Generate Report"
            description="RG will compile a structured narrative report of all findings."
            agentLabel="RG"
            isExecuting={isExecuting}
            onRun={runRG}
          />
        )

      case "complete":
        return (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 80, damping: 16 }}
            className="flex flex-col items-center justify-center h-64 space-y-4 mt-12 bg-green-900/10 border border-green-500/30 rounded-2xl p-8 max-w-2xl mx-auto glass-card-premium"
          >
            <motion.div
              animate={{ scale: [1, 1.15, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              <CheckCircle2 className="w-12 h-12 text-green-400" />
            </motion.div>
            <h3 className="text-2xl font-bold text-green-400">Pipeline Complete</h3>
            <p className="text-[var(--dusty-denim)] text-center">
              All agents have finished execution. Your report and dashboard are ready.
            </p>
          </motion.div>
        )

      default:
        return null
    }
  }

  return (
    <div className="h-full flex flex-col relative">
      <div className="flex-1 overflow-y-auto pb-72 px-4">
        <AnimatePresence mode="wait">
          <motion.div key={currentPhase} {...phaseTransition}>
            {renderPhaseContent()}
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="absolute bottom-0 left-0 right-0 z-50">
        <GlobalAgenticLedger />
      </div>
    </div>
  )
}

function PhaseAction({
  title,
  description,
  agentLabel,
  isExecuting,
  onRun,
}: {
  title: string
  description: string
  agentLabel: string
  isExecuting: boolean
  onRun: () => void
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 80, damping: 16 }}
      className="max-w-2xl mx-auto mt-16 text-center space-y-6"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
        className="inline-block px-3 py-1.5 rounded-lg bg-[var(--prussian-blue)] border border-[var(--dusk-blue)]/30 text-xs font-mono text-[var(--cta-orange)] uppercase tracking-wider"
      >
        {agentLabel}
      </motion.div>

      <motion.h2
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, type: "spring", stiffness: 80 }}
        className="text-3xl font-bold text-[var(--alabaster-grey)]"
      >
        {title}
      </motion.h2>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25 }}
        className="text-[var(--dusty-denim)] max-w-lg mx-auto"
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
        className="inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-[var(--cta-orange)] hover:bg-[var(--cta-orange)]/90 text-white font-semibold transition-all disabled:opacity-50 disabled:pointer-events-none cursor-pointer shadow-lg shadow-[var(--cta-orange)]/20"
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
            Run Agent
          </>
        )}
      </motion.button>
    </motion.div>
  )
}

function LoadingState({ message }: { message: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center h-64 space-y-4"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        className="w-12 h-12 border-4 border-[var(--dusk-blue)] border-t-[var(--cta-orange)] rounded-full"
      />
      <p className="text-[var(--dusty-denim)] font-mono">{message}</p>
    </motion.div>
  )
}
