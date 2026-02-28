"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useSession } from "@/lib/session-context";
import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DatasetUpload } from "@/components/pipeline/DatasetUpload";
import { QuestionBuilder } from "@/components/pipeline/QuestionBuilder";
import { VisualizationGallery } from "@/components/pipeline/VisualizationGallery";
import { KPIDashboard } from "@/components/pipeline/KPIDashboard";
import { ReportView } from "@/components/pipeline/ReportView";
import { MLResultsView } from "@/components/pipeline/MLResultsView";
import { GlobalAgenticLedger } from "@/components/gal/GlobalAgenticLedger";
import { Play, CheckCircle2 } from "lucide-react";

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

function DashboardContent() {
  const router = useRouter();
  const {
    currentPhase,
    isExecuting,
    questions,
    visualizationsData,
    dashboardData,
    reportData,
    mlDetails,
    quickModeAvailable,
    quickModeEnabled,
    setQuickModeEnabled,
    runPhase1a,
    submitUserAnswers,
    runPhase1b,
    runPhase2,
    runFIE,
    runMLRL,
    runVPE,
    runADC,
    runRG,
    runQuickMode,
    runLomProfile,
    runLomTimeline,
    runLomReport,
    advanceFromResults,
    loadSession,
    sessionId,
  } = useSession();

  const searchParams = useSearchParams();
  const sessionQueryId = searchParams.get("session");

  useEffect(() => {
    if (sessionQueryId && sessionQueryId !== sessionId && !isExecuting) {
      loadSession(sessionQueryId);
    }
  }, [sessionQueryId, sessionId, isExecuting, loadSession]);

  const renderPhaseContent = () => {
    switch (currentPhase) {
      case "upload":
        return <DatasetUpload />;

      case "phase1a":
        return (
          <>
            {quickModeAvailable && (
              <div className="max-w-2xl mx-auto mt-10 mb-4 flex items-center justify-center gap-3 rounded-xl border border-[#F97316]/40 bg-[#0A0A0A]/60 px-4 py-3">
                <label
                  htmlFor="quick-mode-toggle"
                  className="flex items-center gap-3 cursor-pointer select-none"
                >
                  <div className="relative">
                    <input
                      type="checkbox"
                      id="quick-mode-toggle"
                      checked={quickModeEnabled}
                      onChange={(e) => setQuickModeEnabled(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 rounded-full bg-[#0A0A0A] border border-white/[0.08] peer-checked:bg-[#F97316]/80 transition-colors" />
                    <div className="absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white/40 peer-checked:translate-x-4 peer-checked:bg-white transition-transform" />
                  </div>
                  <span className="text-xs font-mono uppercase tracking-[0.18em] text-[#F97316]">
                    Fast Mode
                  </span>
                </label>
              </div>
            )}

            <PhaseAction
              title={
                quickModeEnabled
                  ? "Fast Mode — Full Pipeline"
                  : "Profile & Generate Questions"
              }
              description={
                quickModeEnabled
                  ? "All agents will simulate execution using cached analysis for this dataset. This should complete within about 1.5 minutes."
                  : "DPSU will profile your dataset and QBII will generate targeted questions."
              }
              agentLabel={quickModeEnabled ? "ALL AGENTS" : "DPSU + QBII"}
              isExecuting={isExecuting}
              onRun={quickModeEnabled ? runQuickMode : runPhase1a}
            />
          </>
        );

      case "answers":
        return questions.length > 0 ? (
          <QuestionBuilder
            questions={questions.map((q) => ({
              question: (q as Record<string, string>).question || "",
              question_type:
                (q as Record<string, string>).question_type || "goal",
              why_asked: (q as Record<string, string>).why_asked || "",
            }))}
            onSubmit={(answers) => submitUserAnswers(answers)}
          />
        ) : (
          <LoadingState message="Waiting for questions from QBII..." />
        );

      case "phase1b":
        return (
          <PhaseAction
            title="Repair & Explore"
            description="DRIL will repair data integrity issues. EPR will run exploratory analysis."
            agentLabel="DRIL + EPR"
            isExecuting={isExecuting}
            onRun={runPhase1b}
          />
        );

      case "phase2":
        return (
          <PhaseAction
            title="Hypothesis Generation"
            description="IHE will generate analytical hypotheses from exploratory findings."
            agentLabel="IHE"
            isExecuting={isExecuting}
            onRun={runPhase2}
          />
        );

      case "fie":
        return (
          <PhaseAction
            title="Feature Intelligence"
            description="FIE will engineer features using domain knowledge from RAG."
            agentLabel="FIE"
            isExecuting={isExecuting}
            onRun={runFIE}
          />
        );

      case "mlrl":
        return (
          <PhaseAction
            title="Model Training & Evaluation"
            description="ML Engine will build, train, and evaluate predictive models to find the best fit."
            agentLabel="ML Engine"
            isExecuting={isExecuting}
            onRun={runMLRL}
          />
        );

      case "mlrl_results":
        return mlDetails ? (
          <MLResultsView mlDetails={mlDetails} onNext={advanceFromResults} />
        ) : (
          <LoadingState message="Loading ML results..." />
        );

      case "vpe":
        return (
          <PhaseAction
            title="Visualization Planning"
            description="VPE will plan and generate charts from your data findings."
            agentLabel="VPE"
            isExecuting={isExecuting}
            onRun={runVPE}
          />
        );

      case "vpe_results":
        return visualizationsData ? (
          <VisualizationGallery
            visualizations={
              visualizationsData.visualizations as Array<{
                question: string;
                chart_type: string;
                interpretation: string;
                confidence_note: string;
                validation_result: string;
                plotly_config: Record<string, unknown> | null;
                variables_used: string[];
                related_finding: string;
                chart_type_reasoning: string;
                audience_calibration: string;
              }>
            }
            totalRendered={visualizationsData.total_rendered}
            totalFailed={visualizationsData.total_failed}
            overallReasoning={visualizationsData.overall_reasoning}
            onNext={advanceFromResults}
          />
        ) : (
          <LoadingState message="Loading visualizations..." />
        );

      case "adc":
        return (
          <PhaseAction
            title="Analytical Dashboard"
            description="ADC will compose a dashboard with KPIs, alerts, and recommendations."
            agentLabel="ADC"
            isExecuting={isExecuting}
            onRun={runADC}
          />
        );

      case "adc_results":
        return dashboardData ? (
          <KPIDashboard
            kpis={
              dashboardData.kpis as Array<{
                name: string;
                value: string | number;
                justification: string;
                derivation_source: string;
              }>
            }
            alerts={
              dashboardData.alerts as Array<{
                alert_type: string;
                description: string;
                evidence_ref: string;
                confidence: string;
              }>
            }
            recommendations={
              dashboardData.recommendations as Array<{
                action: string;
                target_group: string;
                expected_impact: string;
                urgency: string;
                confidence: string;
                supporting_evidence_ref: string;
                supporting_hypothesis_ref: string;
              }>
            }
            panels={
              dashboardData.panels as Array<{
                panel_name: string;
                description: string;
                elements: unknown[];
              }>
            }
            overallReasoning={dashboardData.overall_reasoning}
            onNext={advanceFromResults}
          />
        ) : (
          <LoadingState message="Loading dashboard..." />
        );

      case "rg":
        return (
          <PhaseAction
            title="Generate Report"
            description="RG will compile a structured narrative report of all findings."
            agentLabel="RG"
            isExecuting={isExecuting}
            onRun={runRG}
          />
        );

      case "rg_results":
        return reportData ? (
          <ReportView
            narrative={reportData.narrative}
            citations={reportData.citations}
            communicatedRecommendations={
              reportData.communicated_recommendations
            }
            stakeholderCalibration={reportData.stakeholder_calibration}
            onNext={advanceFromResults}
          />
        ) : (
          <LoadingState message="Loading report..." />
        );

      case "lom_profile":
        return (
          <PhaseAction
            title="LOM Profiling"
            description="LOM Profiler will parse your logs and extract structured metrics."
            agentLabel="LOM Profiler"
            isExecuting={isExecuting}
            onRun={runLomProfile}
          />
        );

      case "lom_timeline":
        return (
          <PhaseAction
            title="LOM Timeline & RCA"
            description="LOM RCA Engine will reconstruct the incident timeline and propose root causes."
            agentLabel="LOM RCA Engine"
            isExecuting={isExecuting}
            onRun={runLomTimeline}
          />
        );

      case "lom_report":
        return (
          <PhaseAction
            title="LOM Final Report"
            description="LOM Report Gen will compile the findings into a formal RCA report."
            agentLabel="LOM Report Gen"
            isExecuting={isExecuting}
            onRun={runLomReport}
          />
        );

      case "lom_report_results":
        return reportData ? (
          <ReportView
            narrative={reportData.narrative}
            citations={reportData.citations}
            communicatedRecommendations={
              reportData.communicated_recommendations
            }
            stakeholderCalibration={reportData.stakeholder_calibration}
            onNext={advanceFromResults}
          />
        ) : (
          <LoadingState message="Loading LOM report..." />
        );

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
            <h3 className="text-2xl font-bold text-green-400">
              Pipeline Complete
            </h3>
            <p className="text-white/40 text-center">
              All agents have finished execution. Your report and dashboard are
              ready.
            </p>
            <button
              onClick={() => router.push("/dashboard/ml")}
              className="mt-2 inline-flex items-center justify-center px-6 py-3 rounded-xl bg-white/[0.06] hover:bg-white/[0.10] border border-white/[0.08] text-white font-semibold transition-colors"
            >
              Proceed to ML
            </button>
          </motion.div>
        );

      default:
        return null;
    }
  };

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
      className="max-w-2xl mx-auto mt-16 text-center space-y-6"
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
        className="text-3xl font-bold text-white"
      >
        {title}
      </motion.h2>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25 }}
        className="text-white/40 max-w-lg mx-auto"
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
        className="inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-[#F97316] hover:bg-[#EA580C] text-white font-semibold transition-all disabled:opacity-50 disabled:pointer-events-none cursor-pointer shadow-lg shadow-[#F97316]/20"
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
  );
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
        className="w-12 h-12 border-4 border-white/[0.06] border-t-[#F97316] rounded-full"
      />
      <p className="text-white/40 font-mono">{message}</p>
    </motion.div>
  );
}
