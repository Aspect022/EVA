"use client"

import { useSession } from "@/lib/session-context"
import { DatasetUpload } from "@/components/pipeline/DatasetUpload"
import { QuestionBuilder } from "@/components/pipeline/QuestionBuilder"
import { GlobalAgenticLedger } from "@/components/gal/GlobalAgenticLedger"
import { Play, CheckCircle2 } from "lucide-react"

export default function DashboardPage() {
  const {
    currentPhase,
    isExecuting,
    questions,
    hypotheses,
    features,
    dashboardStats,
    report,
    runPhase1a,
    submitUserAnswers,
    runPhase1b,
    runPhase2,
    runFIE,
    runVPE,
    runADC,
    runRG,
  } = useSession()

  const renderPhaseContent = () => {
    switch (currentPhase) {
      case "upload":
        return <DatasetUpload />

      case "phase1a":
        return (
          <PhaseAction
            title="Profile & Generate Questions"
            description="DPSU will profile your dataset and QBII will generate targeted questions."
            agentLabel="DPSU + QBII"
            isExecuting={isExecuting}
            onRun={runPhase1a}
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
          <div className="flex flex-col items-center justify-center h-64 space-y-4 mt-12 bg-green-900/10 border border-green-500/30 rounded-xl p-8 max-w-2xl mx-auto">
            <CheckCircle2 className="w-12 h-12 text-green-400" />
            <h3 className="text-2xl font-bold text-green-400">Pipeline Complete</h3>
            <p className="text-[var(--dusty-denim)] text-center">
              All agents have finished execution. Your report and dashboard are ready.
            </p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="h-full flex flex-col relative">
      <div className="flex-1 overflow-y-auto pb-72 px-4">
        {renderPhaseContent()}
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
    <div className="max-w-2xl mx-auto mt-16 text-center space-y-6">
      <div className="inline-block px-3 py-1 rounded bg-[var(--prussian-blue)] border border-[var(--dusk-blue)] text-xs font-mono text-[var(--dusty-denim)] uppercase tracking-wider">
        {agentLabel}
      </div>
      <h2 className="text-3xl font-bold text-[var(--alabaster-grey)]">{title}</h2>
      <p className="text-[var(--dusty-denim)] max-w-lg mx-auto">{description}</p>
      <button
        onClick={onRun}
        disabled={isExecuting}
        className="inline-flex items-center gap-3 px-8 py-4 rounded-lg bg-[var(--dusk-blue)] hover:bg-[var(--dusty-denim)] text-[var(--alabaster-grey)] font-semibold transition-all disabled:opacity-50 disabled:pointer-events-none"
      >
        {isExecuting ? (
          <>
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Executing...
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            Run Agent
          </>
        )}
      </button>
    </div>
  )
}

function LoadingState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 space-y-4">
      <div className="w-12 h-12 border-4 border-[var(--dusk-blue)] border-t-[var(--dusty-denim)] rounded-full animate-spin" />
      <p className="text-[var(--dusty-denim)] font-mono">{message}</p>
    </div>
  )
}
