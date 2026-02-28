"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import {
  api,
  type QuickModeEvent,
  type VisualizationsData,
  type DashboardData,
  type ReportData,
} from "./api-client";
import {
  titanicQuestions,
  titanicVisualizationsData,
  titanicDashboardData,
  titanicReportData,
} from "./demo-titanic";

// Pipeline phases in order
export const PIPELINE_PHASES = [
  { id: "upload", label: "Upload Dataset", agent: "System" },
  { id: "phase1a", label: "Profile & Questions", agent: "DPSU + QBII" },
  { id: "answers", label: "Confirm Intent", agent: "QBII" },
  { id: "phase1b", label: "Repair & Explore", agent: "DRIL + EPR" },
  { id: "phase2", label: "Hypotheses", agent: "IHE" },
  { id: "fie", label: "Feature Intelligence", agent: "FIE" },
  { id: "vpe", label: "Visualizations", agent: "VPE" },
  { id: "vpe_results", label: "Viz Results", agent: "VPE" },
  { id: "adc", label: "Dashboard", agent: "ADC" },
  { id: "adc_results", label: "Dashboard Results", agent: "ADC" },
  { id: "rg", label: "Final Report", agent: "RG" },
  { id: "rg_results", label: "Report View", agent: "RG" },
  // LOM specific phases
  { id: "lom_profile", label: "LOM Profile", agent: "LOM Profiler" },
  { id: "lom_timeline", label: "Timeline & RCA", agent: "LOM RCA Engine" },
  { id: "lom_report", label: "Final LOM Report", agent: "LOM Report Gen" },
  {
    id: "lom_report_results",
    label: "LOM Report View",
    agent: "LOM Report Gen",
  },
  { id: "complete", label: "Complete", agent: "—" },
] as const;

export type PhaseId = (typeof PIPELINE_PHASES)[number]["id"];

export interface LogEntry {
  timestamp: string;
  agent: string;
  message: string;
  type: "info" | "success" | "warn" | "error";
}

export type RulesMode = "full" | "lite";

interface SessionState {
  sessionId: string | null;
  csvFileName: string | null;
  currentPhase: PhaseId;
  isExecuting: boolean;
  rulesMode: RulesMode;
  logs: LogEntry[];
  // Quick Mode
  quickModeAvailable: boolean;
  quickModeEnabled: boolean;
  sourceSessionId: string | null;
  completedPhases: string[];
  // Phase-specific results
  questions: Array<Record<string, unknown>>;
  intent: { primary_objective?: string; selected_target?: string } | null;
  hypotheses: Array<Record<string, unknown>>;
  features: Array<Record<string, unknown>>;
  visualizations: Array<Record<string, unknown>>;
  visualizationsData: VisualizationsData | null;
  dashboardStats: {
    panels: number;
    kpis: number;
    alerts: number;
    recommendations: number;
  } | null;
  dashboardData: DashboardData | null;
  report: Record<string, unknown> | null;
  reportData: ReportData | null;
  mlDetails: Record<string, unknown> | null;
  // LOM Pipeline
  isLom: boolean;
  lomGalData: Record<string, unknown> | null;
}

interface SessionContextType extends SessionState {
  addLog: (agent: string, message: string, type: LogEntry["type"]) => void;
  createAndUpload: (file: File) => Promise<void>;
  runPhase1a: () => Promise<void>;
  submitUserAnswers: (answers: Record<string, string>) => Promise<void>;
  runPhase1b: () => Promise<void>;
  runPhase2: () => Promise<void>;
  runFIE: () => Promise<void>;
  runMLRL: () => Promise<void>;
  runVPE: () => Promise<void>;
  runADC: () => Promise<void>;
  runRG: () => Promise<void>;
  runQuickMode: () => Promise<void>;
  runLomProfile: () => Promise<void>;
  runLomTimeline: () => Promise<void>;
  runLomReport: () => Promise<void>;
  advanceFromResults: () => void;
  resetSession: () => void;
  getNextAgentName: () => string;
  setRulesMode: (mode: RulesMode) => void;
  setQuickModeEnabled: (enabled: boolean) => void;
  loadSession: (sessionId: string) => Promise<void>;
}

const SessionContext = createContext<SessionContextType | null>(null);

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}

const initialState: SessionState = {
  sessionId: null,
  csvFileName: null,
  currentPhase: "upload",
  isExecuting: false,
  rulesMode: "full",
  logs: [],
  quickModeAvailable: false,
  quickModeEnabled: false,
  sourceSessionId: null,
  completedPhases: [],
  questions: [],
  intent: null,
  hypotheses: [],
  features: [],
  visualizations: [],
  visualizationsData: null,
  dashboardStats: null,
  dashboardData: null,
  report: null,
  reportData: null,
  mlDetails: null,
  isLom: false,
  lomGalData: null,
};

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export function SessionProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SessionState>(initialState);

  const addLog = useCallback(
    (agent: string, message: string, type: LogEntry["type"]) => {
      setState((prev) => ({
        ...prev,
        logs: [
          ...prev.logs,
          { timestamp: new Date().toLocaleTimeString(), agent, message, type },
        ],
      }));
    },
    [],
  );

  const setPhase = useCallback((phase: PhaseId) => {
    setState((prev) => ({ ...prev, currentPhase: phase }));
  }, []);

  const setExecuting = useCallback((v: boolean) => {
    setState((prev) => ({ ...prev, isExecuting: v }));
  }, []);

  const createAndUpload = useCallback(
    async (file: File) => {
      setExecuting(true);
      try {
        addLog("SYSTEM", "Creating session...", "info");
        const session = await api.createSession();
        setState((prev) => ({ ...prev, sessionId: session.session_id }));
        addLog(
          "SYSTEM",
          `Session ${session.session_id.slice(0, 8)}... created`,
          "success",
        );

        addLog("SYSTEM", `Uploading ${file.name}...`, "info");

        let uploadResult;
        const isLomUpload = !file.name.toLowerCase().endsWith(".csv");

        if (isLomUpload) {
          uploadResult = await api.uploadLomDataset(session.session_id, [file]);
        } else {
          uploadResult = await api.uploadDataset(session.session_id, file);
        }

        setState((prev) => ({
          ...prev,
          csvFileName: file.name,
          isLom: isLomUpload,
          // Reset any previous fast/quick mode hints for this new upload
          quickModeAvailable: false,
          quickModeEnabled: false,
          sourceSessionId: null,
          completedPhases: [],
        }));

        addLog(
          "SYSTEM",
          `File "${file.name}" uploaded successfully`,
          "success",
        );

        // Check if this dataset was previously analyzed (Quick Mode)
        try {
          const check = await api.checkDataset(session.session_id);
          if (check.quick_mode_available) {
            setState((prev) => ({
              ...prev,
              quickModeAvailable: true,
              sourceSessionId: check.source_session_id,
              completedPhases: check.completed_phases,
            }));
            addLog(
              "SYSTEM",
              "Cached analysis detected — Quick Mode available",
              "info",
            );
          } else {
            // Fallback: infer previous runs by filename from session list.
            // Prefer the richest prior session (report > dashboard > visualizations > features > hypotheses > findings > intent > identity).
            const sessions = await api.listSessions();
            const candidates = sessions.filter(
              (s) =>
                s.session_id !== session.session_id &&
                s.csv_file === file.name &&
                (s.has_report ||
                  s.has_dashboard ||
                  s.has_visualizations ||
                  s.has_features ||
                  s.has_hypotheses ||
                  s.has_findings ||
                  s.has_intent ||
                  s.has_identity),
            );

            if (candidates.length) {
              const scored = candidates
                .map((s) => ({
                  session: s,
                  score:
                    (s.has_report ? 128 : 0) +
                    (s.has_dashboard ? 64 : 0) +
                    (s.has_visualizations ? 32 : 0) +
                    (s.has_features ? 16 : 0) +
                    (s.has_hypotheses ? 8 : 0) +
                    (s.has_findings ? 4 : 0) +
                    (s.has_intent ? 2 : 0) +
                    (s.has_identity ? 1 : 0),
                }))
                .sort((a, b) => b.score - a.score);

              const best = scored[0].session;

              setState((prev) => ({
                ...prev,
                quickModeAvailable: true,
                sourceSessionId: best.session_id,
              }));
              addLog(
                "SYSTEM",
                `Previous analysis detected for this dataset (session ${best.session_id.slice(0, 8)}...). Fast Mode available.`,
                "info",
              );
            }
          }
        } catch {
          /* silently skip if check fails */
        }

        if (isLomUpload) {
          setPhase("lom_profile");
        } else {
          setPhase("phase1a");
        }
      } catch (err: unknown) {
        addLog(
          "SYSTEM",
          `Upload failed: ${err instanceof Error ? err.message : String(err)}`,
          "error",
        );
      } finally {
        setExecuting(false);
      }
    },
    [addLog, setPhase, setExecuting],
  );

  const runPhase1a = useCallback(async () => {
    if (!state.sessionId || !state.csvFileName) return;
    setExecuting(true);
    try {
      addLog("DPSU", "Running dataset profiling...", "info");
      addLog("QBII", "Generating targeted questions...", "info");
      const res = await api.executePhase1a(
        state.sessionId,
        state.csvFileName,
        state.rulesMode,
      );
      setState((prev) => ({ ...prev, questions: res.questions }));
      addLog(
        "QBII",
        `Generated ${res.questions.length} question(s)`,
        "success",
      );
      setPhase("answers");
    } catch (err: unknown) {
      addLog(
        "DPSU",
        `Phase 1a failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [state.sessionId, state.csvFileName, addLog, setPhase, setExecuting]);

  const submitUserAnswers = useCallback(
    async (answers: Record<string, string>) => {
      if (!state.sessionId) return;
      const isTitanicFast =
        state.quickModeEnabled &&
        state.csvFileName?.toLowerCase().includes("titanic");
      setExecuting(true);
      try {
        addLog("QBII", "Processing user intent...", "info");
        if (isTitanicFast) {
          await sleep(1200);
          const primary = Object.values(answers)[0] as string | undefined;
          setState((prev) => ({
            ...prev,
            intent: {
              primary_objective:
                primary ?? "Understand survival patterns on the Titanic",
              selected_target: "Passenger survival probability",
            },
          }));
          addLog(
            "QBII",
            "Intent confirmed for Titanic demo analysis",
            "success",
          );
          setPhase("phase1b");
        } else {
          const res = await api.submitAnswers(
            state.sessionId,
            answers,
            state.rulesMode,
          );
          setState((prev) => ({
            ...prev,
            intent: {
              primary_objective: res.primary_objective ?? undefined,
              selected_target: res.selected_target ?? undefined,
            },
          }));
          addLog(
            "QBII",
            `Intent confirmed: ${res.primary_objective}`,
            "success",
          );
          setPhase("phase1b");
        }
      } catch (err: unknown) {
        addLog(
          "QBII",
          `Answer submission failed: ${err instanceof Error ? err.message : String(err)}`,
          "error",
        );
      } finally {
        setExecuting(false);
      }
    },
    [
      state.sessionId,
      state.quickModeEnabled,
      state.csvFileName,
      state.rulesMode,
      addLog,
      setPhase,
      setExecuting,
    ],
  );

  const runPhase1b = useCallback(async () => {
    if (!state.sessionId || !state.csvFileName) return;
    const isTitanicFast =
      state.quickModeEnabled &&
      state.csvFileName.toLowerCase().includes("titanic");
    setExecuting(true);
    try {
      addLog("DRIL", "Running data repair & integrity checks...", "info");
      addLog("EPR", "Running exploratory analysis...", "info");
      if (isTitanicFast) {
        // Simulate longer data repair/exploration time for Titanic demo
        await sleep(30_000);
        addLog("EPR", "Exploration complete (Titanic demo)", "success");
      } else {
        await api.executePhase1b(
          state.sessionId,
          state.csvFileName,
          state.rulesMode,
        );
        addLog("EPR", "Exploration complete", "success");
      }
      setPhase("phase2");
    } catch (err: unknown) {
      addLog(
        "DRIL",
        `Phase 1b failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [
    state.sessionId,
    state.csvFileName,
    state.quickModeEnabled,
    state.rulesMode,
    addLog,
    setPhase,
    setExecuting,
  ]);

  const runPhase2 = useCallback(async () => {
    if (!state.sessionId) return;
    const isTitanicFast =
      state.quickModeEnabled &&
      state.csvFileName?.toLowerCase().includes("titanic");
    setExecuting(true);
    try {
      addLog("IHE", "Generating hypotheses from findings...", "info");
      if (isTitanicFast) {
        await sleep(2800);
        setState((prev) => ({ ...prev, hypotheses: [] }));
        addLog(
          "IHE",
          "Generated hypotheses for Titanic demo (omitted from UI)",
          "success",
        );
      } else {
        const res = await api.executePhase2(state.sessionId, state.rulesMode);
        setState((prev) => ({ ...prev, hypotheses: res.hypotheses }));
        addLog(
          "IHE",
          `Generated ${res.hypotheses_count} hypothesis(es)`,
          "success",
        );
      }
      setPhase("fie");
    } catch (err: unknown) {
      addLog(
        "IHE",
        `Phase 2 failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [
    state.sessionId,
    state.quickModeEnabled,
    state.csvFileName,
    state.rulesMode,
    addLog,
    setPhase,
    setExecuting,
  ]);

  const runFIE = useCallback(async () => {
    if (!state.sessionId) return;
    const isTitanicFast =
      state.quickModeEnabled &&
      state.csvFileName?.toLowerCase().includes("titanic");
    setExecuting(true);
    try {
      addLog("FIE", "Running feature intelligence engine...", "info");
      if (isTitanicFast) {
        await sleep(2600);
        setState((prev) => ({ ...prev, features: [] }));
        addLog(
          "FIE",
          "Engineered feature plan for Titanic demo (summarized in GAL)",
          "success",
        );
      } else {
        const res = await api.executeFIE(state.sessionId, state.rulesMode);
        setState((prev) => ({ ...prev, features: res.features }));
        addLog("FIE", `Engineered ${res.features_count} feature(s)`, "success");
      }
      setPhase("vpe");
    } catch (err: unknown) {
      addLog(
        "FIE",
        `FIE failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [
    state.sessionId,
    state.quickModeEnabled,
    state.csvFileName,
    state.rulesMode,
    addLog,
    setPhase,
    setExecuting,
  ]);

  const runMLRL = useCallback(async () => {
    if (!state.sessionId) return;
    const isTitanicFast =
      state.quickModeEnabled &&
      state.csvFileName?.toLowerCase().includes("titanic");
    setExecuting(true);
    try {
      addLog(
        "ML Engine",
        "Training and evaluating candidate machine learning models...",
        "info",
      );
      if (isTitanicFast) {
        await sleep(2600);
        setState((prev) => ({
          ...prev,
          mlDetails: {
            selected_model: "RandomForestClassifier",
            metrics: { Accuracy: 0.85, "F1-Score": 0.84 },
          },
        }));
        addLog(
          "ML Engine",
          "Trained Random Forest model for titanic survival demo",
          "success",
        );
      } else {
        const res = await api.executeMLRL(state.sessionId, state.rulesMode);
        if (res.status === "ML Not Required") {
          addLog(
            "ML Engine",
            "ML not required for this analysis. Skipping.",
            "info",
          );
        } else {
          addLog(
            "ML Engine",
            `Selected best model: ${res.ml.selected_model}`,
            "success",
          );
          setState((prev) => ({ ...prev, mlDetails: res.ml }));
        }
      }
    } catch (err: unknown) {
      addLog(
        "ML Engine",
        `ML training failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [
    state.sessionId,
    state.quickModeEnabled,
    state.csvFileName,
    state.rulesMode,
    addLog,
    setPhase,
    setExecuting,
  ]);

  const runVPE = useCallback(async () => {
    if (!state.sessionId) return;
    const isTitanicFast =
      state.quickModeEnabled &&
      state.csvFileName?.toLowerCase().includes("titanic");
    setExecuting(true);
    try {
      addLog("VPE", "Planning and generating visualizations...", "info");
      if (isTitanicFast) {
        await sleep(3200);
        setState((prev) => ({
          ...prev,
          visualizations: titanicVisualizationsData.visualizations,
          visualizationsData: titanicVisualizationsData,
        }));
        addLog(
          "VPE",
          `Created ${titanicVisualizationsData.total_rendered} visualization(s) for Titanic demo`,
          "success",
        );
      } else {
        const res = await api.executeVPE(state.sessionId, state.rulesMode);
        setState((prev) => ({ ...prev, visualizations: res.visualizations }));
        addLog(
          "VPE",
          `Created ${res.visualizations_count} visualization(s)`,
          "success",
        );

        // Fetch full visualization data with plotly_config
        try {
          const vizData = await api.getVisualizations(state.sessionId);
          setState((prev) => ({ ...prev, visualizationsData: vizData }));
        } catch {
          /* fallback: show results without charts */
        }
      }

      setPhase("vpe_results");
    } catch (err: unknown) {
      addLog(
        "VPE",
        `VPE failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [
    state.sessionId,
    state.quickModeEnabled,
    state.csvFileName,
    state.rulesMode,
    addLog,
    setPhase,
    setExecuting,
  ]);

  const runADC = useCallback(async () => {
    if (!state.sessionId) return;
    const isTitanicFast =
      state.quickModeEnabled &&
      state.csvFileName?.toLowerCase().includes("titanic");
    setExecuting(true);
    try {
      addLog("ADC", "Composing analytical dashboard...", "info");
      if (isTitanicFast) {
        await sleep(2800);
        setState((prev) => ({
          ...prev,
          dashboardStats: {
            panels: titanicDashboardData.panels.length,
            kpis: titanicDashboardData.kpis.length,
            alerts: titanicDashboardData.alerts.length,
            recommendations: titanicDashboardData.recommendations.length,
          },
          dashboardData: titanicDashboardData,
        }));
        addLog(
          "ADC",
          `Dashboard ready for Titanic demo: ${titanicDashboardData.kpis.length} KPIs, ${titanicDashboardData.recommendations.length} recommendations`,
          "success",
        );
      } else {
        const res = await api.executeADC(state.sessionId, state.rulesMode);
        setState((prev) => ({
          ...prev,
          dashboardStats: {
            panels: res.panels,
            kpis: res.kpis,
            alerts: res.alerts,
            recommendations: res.recommendations,
          },
        }));
        addLog(
          "ADC",
          `Dashboard ready: ${res.panels} panels, ${res.kpis} KPIs`,
          "success",
        );

        // Fetch full dashboard data with content
        try {
          const dashData = await api.getDashboard(state.sessionId);
          setState((prev) => ({ ...prev, dashboardData: dashData }));
        } catch {
          /* fallback: show summary only */
        }
      }

      setPhase("adc_results");
    } catch (err: unknown) {
      addLog(
        "ADC",
        `ADC failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [
    state.sessionId,
    state.quickModeEnabled,
    state.csvFileName,
    state.rulesMode,
    addLog,
    setPhase,
    setExecuting,
  ]);

  const runRG = useCallback(async () => {
    if (!state.sessionId) return;
    const isTitanicFast =
      state.quickModeEnabled &&
      state.csvFileName?.toLowerCase().includes("titanic");
    setExecuting(true);
    try {
      addLog("RG", "Generating final report...", "info");
      if (isTitanicFast) {
        await sleep(3000);
        setState((prev) => ({
          ...prev,
          report: { narrative: titanicReportData.narrative },
          reportData: titanicReportData,
        }));
        addLog("RG", "Titanic demo report generated successfully", "success");
      } else {
        const res = await api.executeRG(state.sessionId, state.rulesMode);
        setState((prev) => ({ ...prev, report: res.report }));
        addLog("RG", "Report generated successfully", "success");

        // Fetch full report data
        try {
          const reportData = await api.getReport(state.sessionId);
          setState((prev) => ({ ...prev, reportData }));
        } catch {
          /* fallback */
        }
      }

      setPhase("rg_results");
    } catch (err: unknown) {
      addLog(
        "RG",
        `Report generation failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [
    state.sessionId,
    state.quickModeEnabled,
    state.csvFileName,
    state.rulesMode,
    addLog,
    setPhase,
    setExecuting,
  ]);

  const runLomProfile = useCallback(async () => {
    if (!state.sessionId) return;
    setExecuting(true);
    try {
      addLog("LOM Profiler", "Running LOM Log & Metric profiling...", "info");
      await api.executeLomProfile(state.sessionId);
      addLog("LOM Profiler", "LOM Profiling complete", "success");

      const galData = await api.getLomGal(state.sessionId);
      setState((prev) => ({ ...prev, lomGalData: galData }));

      setPhase("lom_timeline");
    } catch (err: unknown) {
      addLog(
        "LOM Profiler",
        `LOM Profile failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [state.sessionId, addLog, setPhase, setExecuting]);

  const runLomTimeline = useCallback(async () => {
    if (!state.sessionId) return;
    setExecuting(true);
    try {
      addLog(
        "LOM RCA",
        "Reconstructing timeline & generating hypotheses...",
        "info",
      );
      await api.executeLomTimeline(state.sessionId);
      addLog("LOM RCA", "Timeline & Hypothesis generation complete", "success");

      const galData = await api.getLomGal(state.sessionId);
      setState((prev) => ({ ...prev, lomGalData: galData }));

      setPhase("lom_report");
    } catch (err: unknown) {
      addLog(
        "LOM RCA",
        `Timeline & RCA failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [state.sessionId, addLog, setPhase, setExecuting]);

  const runLomReport = useCallback(async () => {
    if (!state.sessionId) return;
    setExecuting(true);
    try {
      addLog("LOM Report", "Generating final LOM report...", "info");
      await api.executeLomReport(state.sessionId);
      addLog("LOM Report", "LOM Report complete", "success");

      const galData = await api.getLomGal(state.sessionId);
      const rca = galData.rca_report as any;

      const mappedReport: ReportData = {
        narrative: `# Executive Summary\n${rca?.executive_summary || ""}\n\n# Root Cause\n${rca?.root_cause || ""}\n\n# Timeline Narrative\n${rca?.incident_timeline_narrative || ""}\n\n# Impact Assessment\n${rca?.impact_assessment || ""}`,
        citations: rca?.citations || [],
        included_visualizations: [],
        communicated_recommendations: (rca?.remediation_steps || []).map(
          (step: any) =>
            `[${step.priority}] ${step.action}: ${step.estimated_impact}`,
        ),
        stakeholder_calibration: `Confidence: ${rca?.confidence_level || "Unknown"}`,
      };

      setState((prev) => ({
        ...prev,
        lomGalData: galData,
        reportData: mappedReport,
      }));

      setPhase("lom_report_results");
    } catch (err: unknown) {
      addLog(
        "LOM Report",
        `Report generation failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [state.sessionId, addLog, setPhase, setExecuting]);

  const resetSession = useCallback(() => {
    setState(initialState);
  }, []);

  const loadSession = useCallback(
    async (sessionId: string) => {
      setExecuting(true);
      try {
        addLog("SYSTEM", `Loading session ${sessionId.slice(0, 8)}...`, "info");
        const sessions = await api.listSessions();
        const session = sessions.find((s) => s.session_id === sessionId);
        if (!session) throw new Error("Session not found");

        setState((prev) => ({
          ...prev,
          sessionId,
          csvFileName: session.csv_file,
        }));

        // Determine phase from the session info
        let targetPhase: PhaseId = "upload";

        // Check LOM first
        if (session.has_lom_report) targetPhase = "lom_report_results";
        else if (session.has_lom_rca) targetPhase = "lom_report";
        else if (session.has_lom_timeline) targetPhase = "lom_timeline";
        else if (session.has_lom_profile || session.has_lom_data)
          targetPhase = "lom_profile";
        // Standard CSV path
        else if (session.has_report) targetPhase = "rg_results";
        else if (session.has_dashboard) targetPhase = "adc_results";
        else if (session.has_visualizations) targetPhase = "vpe_results";
        else if (session.has_features) targetPhase = "vpe";
        else if (session.has_hypotheses) targetPhase = "fie";
        else if (session.has_findings || session.has_integrity)
          targetPhase = "phase2";
        else if (session.has_intent) targetPhase = "phase1b";
        else if (session.has_identity) targetPhase = "answers";

        setState((prev) => ({ ...prev, currentPhase: targetPhase }));

        // Load necessary data based on the phase
        if (
          ["rg_results", "adc_results", "vpe_results"].includes(targetPhase)
        ) {
          try {
            const viz = await api.getVisualizations(sessionId);
            setState((prev) => ({
              ...prev,
              visualizationsData: viz,
              visualizations: viz.visualizations,
            }));
          } catch {}
          try {
            const dash = await api.getDashboard(sessionId);
            setState((prev) => ({
              ...prev,
              dashboardData: dash,
              dashboardStats: {
                panels: dash.panels.length,
                kpis: dash.kpis.length,
                alerts: dash.alerts.length,
                recommendations: dash.recommendations.length,
              },
            }));
          } catch {}
          try {
            const rep = await api.getReport(sessionId);
            setState((prev) => ({
              ...prev,
              reportData: rep,
              report: rep as unknown as Record<string, unknown>,
            }));
          } catch {}
          if (session.has_mlrl) {
            try {
              const gal = await api.getGAL(sessionId);
              if (
                (gal as any).candidate_models &&
                (gal as any).candidate_models.selected_model
              ) {
                const model = (gal as any).candidate_models.selected_model;
                const evalRec = (
                  (gal as any).model_evaluation?.evaluation_results || []
                ).find((e: any) => e.model_id === model.id);
                setState((prev) => ({
                  ...prev,
                  mlDetails: {
                    selected_model: model.model_name,
                    metrics: evalRec?.metrics || {},
                  },
                }));
              }
            } catch {}
          }
        } else if (targetPhase === "lom_report_results") {
          try {
            const gal = await api.getLomGal(sessionId);
            setState((prev) => ({ ...prev, lomGalData: gal }));
            // also map report
            const rca = gal.rca_report as any;
            if (rca) {
              const mappedReport: ReportData = {
                narrative: `# Executive Summary\n${rca.executive_summary || ""}\n\n# Root Cause\n${rca.root_cause || ""}\n\n# Timeline Narrative\n${rca.incident_timeline_narrative || ""}\n\n# Impact Assessment\n${rca.impact_assessment || ""}`,
                citations: rca.citations || [],
                included_visualizations: [],
                communicated_recommendations: (rca.remediation_steps || []).map(
                  (step: any) =>
                    `[${step.priority}] ${step.action}: ${step.estimated_impact}`,
                ),
                stakeholder_calibration: `Confidence: ${rca.confidence_level || "Unknown"}`,
              };
              setState((prev) => ({ ...prev, reportData: mappedReport }));
            }
          } catch {}
        } else if (targetPhase === "answers") {
          try {
            const gal = await api.getGAL(sessionId);
            if (
              gal.user_intent &&
              (gal.user_intent as any).generated_questions
            ) {
              setState((prev) => ({
                ...prev,
                questions: (gal.user_intent as any)
                  .generated_questions as Array<Record<string, unknown>>,
              }));
            }
          } catch {}
        }

        addLog("SYSTEM", "Session loaded successfully", "success");
      } catch (err: unknown) {
        addLog(
          "SYSTEM",
          `Failed to load session: ${err instanceof Error ? err.message : String(err)}`,
          "error",
        );
      } finally {
        setExecuting(false);
      }
    },
    [addLog, setExecuting],
  );

  const advanceFromResults = useCallback(() => {
    const isTitanicFast =
      state.quickModeEnabled &&
      !!state.csvFileName &&
      state.csvFileName.toLowerCase().includes("titanic");

    if (state.currentPhase === "vpe_results") {
      // In Fast Mode we already have dashboard/report content prepared,
      // so "Next" should advance through the result slides directly if data is available.
      if ((isTitanicFast || state.quickModeEnabled) && state.dashboardData)
        setPhase("adc_results");
      else setPhase("adc");
      return;
    }

    if (state.currentPhase === "adc_results") {
      if ((isTitanicFast || state.quickModeEnabled) && state.reportData)
        setPhase("rg_results");
      else setPhase("rg");
      return;
    } else if (
      state.currentPhase === "rg_results" ||
      state.currentPhase === "lom_report_results"
    ) {
      setPhase("complete");
    }
  }, [
    state.currentPhase,
    state.quickModeEnabled,
    state.csvFileName,
    state.dashboardData,
    state.reportData,
    setPhase,
  ]);

  const getNextAgentName = useCallback(() => {
    const idx = PIPELINE_PHASES.findIndex((p) => p.id === state.currentPhase);
    if (idx < 0 || idx >= PIPELINE_PHASES.length) return "—";
    return PIPELINE_PHASES[idx].agent;
  }, [state.currentPhase]);

  const setRulesMode = useCallback((mode: RulesMode) => {
    setState((prev) => ({ ...prev, rulesMode: mode }));
  }, []);

  const setQuickModeEnabled = useCallback((enabled: boolean) => {
    setState((prev) => ({ ...prev, quickModeEnabled: enabled }));
  }, []);

  // Maps phase IDs from the backend to the frontend PhaseId type
  const PHASE_MAP: Record<string, PhaseId> = {
    phase1a: "answers",
    answers: "phase1b",
    phase1b: "phase2",
    phase2: "fie",
    fie: "vpe",
    vpe: "adc",
    adc: "rg",
    rg: "complete",
  };

  const runQuickMode = useCallback(async () => {
    if (!state.sessionId) return;

    const isTitanicFast =
      state.quickModeEnabled &&
      state.csvFileName &&
      state.csvFileName.toLowerCase().includes("titanic");

    if (isTitanicFast) {
      setExecuting(true);
      try {
        addLog(
          "SYSTEM",
          "Fast Mode (Titanic demo) activated — simulating full pipeline...",
          "info",
        );

        // Phase 1a demo
        addLog(
          "DPSU",
          "Loading Titanic manifest and profiling schema...",
          "info",
        );
        await sleep(1200);
        addLog(
          "QBII",
          "Generating targeted questions for Titanic analysis...",
          "info",
        );
        await sleep(1200);

        setState((prev) => ({
          ...prev,
          questions: titanicQuestions,
          visualizations: titanicVisualizationsData.visualizations,
          visualizationsData: titanicVisualizationsData,
          dashboardStats: {
            panels: titanicDashboardData.panels.length,
            kpis: titanicDashboardData.kpis.length,
            alerts: titanicDashboardData.alerts.length,
            recommendations: titanicDashboardData.recommendations.length,
          },
          dashboardData: titanicDashboardData,
          report: { narrative: titanicReportData.narrative },
          reportData: titanicReportData,
        }));

        addLog(
          "SYSTEM",
          `Fast Mode prepared ${titanicVisualizationsData.total_rendered} charts, ${titanicDashboardData.kpis.length} KPIs, and a narrative report.`,
          "success",
        );

        setPhase("answers");
      } catch (err: unknown) {
        addLog(
          "SYSTEM",
          `Fast Mode (Titanic demo) failed: ${err instanceof Error ? err.message : String(err)}`,
          "error",
        );
      } finally {
        setExecuting(false);
      }
      return;
    }

    if (!state.sourceSessionId) return;
    setExecuting(true);
    try {
      addLog(
        "SYSTEM",
        "Quick Mode activated — replaying cached analysis...",
        "info",
      );
      let lastSimulatedPhase = "";
      await api.streamQuickMode(
        state.sessionId,
        state.sourceSessionId,
        (event: QuickModeEvent) => {
          if (event.type === "log") {
            const logType =
              event.log_type === "success" ||
              event.log_type === "error" ||
              event.log_type === "warn" ||
              event.log_type === "info"
                ? (event.log_type as LogEntry["type"])
                : "info";
            addLog(event.agent || "SYSTEM", event.message || "", logType);
          } else if (event.type === "phase_result" && event.phase) {
            const phase = event.phase as string;
            lastSimulatedPhase = phase;
            // Update state based on which phase completed
            if (phase === "phase1a" && event.questions) {
              setState((prev) => ({
                ...prev,
                questions: event.questions as Array<Record<string, unknown>>,
              }));
            } else if (phase === "answers") {
              setState((prev) => ({
                ...prev,
                intent: {
                  primary_objective: event.primary_objective as
                    | string
                    | undefined,
                  selected_target: event.selected_target as string | undefined,
                },
              }));
            } else if (phase === "phase2" && event.hypotheses) {
              setState((prev) => ({
                ...prev,
                hypotheses: event.hypotheses as Array<Record<string, unknown>>,
              }));
            } else if (phase === "fie" && event.features) {
              setState((prev) => ({
                ...prev,
                features: event.features as Array<Record<string, unknown>>,
              }));
            } else if (phase === "mlrl" && event.ml) {
              setState((prev) => ({
                ...prev,
                mlDetails: event.ml as Record<string, unknown>,
              }));
            } else if (phase === "vpe" && event.visualizations) {
              setState((prev) => ({
                ...prev,
                visualizations: event.visualizations as Array<
                  Record<string, unknown>
                >,
              }));
            } else if (phase === "adc") {
              setState((prev) => ({
                ...prev,
                dashboardStats: {
                  panels: (event.panels as number) || 0,
                  kpis: (event.kpis as number) || 0,
                  alerts: (event.alerts as number) || 0,
                  recommendations: (event.recommendations as number) || 0,
                },
              }));
            } else if (phase === "rg" && event.report) {
              setState((prev) => ({
                ...prev,
                report: event.report as Record<string, unknown>,
              }));
            }
            // Advance to the next phase
            const nextPhase = PHASE_MAP[phase];
            if (nextPhase && nextPhase !== "complete") setPhase(nextPhase);
          } else if (event.type === "done") {
            addLog(
              "SYSTEM",
              "Quick Mode complete — all phases simulated",
              "success",
            );
            // In Fast Mode, always provide a set of premade questions so the UI can proceed.
            const fastModeQuestions: Array<Record<string, unknown>> = [
              {
                question:
                  "What are the key drivers of the main outcome in this dataset?",
                question_type: "goal",
                why_asked:
                  "Helps EVA focus the analysis on the variables that most strongly influence your target.",
              },
              {
                question:
                  "Which segments or cohorts behave most differently in this data?",
                question_type: "stakeholder",
                why_asked:
                  "Surfaces important subgroups where performance, risk, or behavior diverges.",
              },
              {
                question:
                  "What trends or patterns over time matter most for this dataset?",
                question_type: "time",
                why_asked:
                  "Highlights temporal structure like seasonality, drift, or regime changes.",
              },
              {
                question:
                  "What constraints or business rules should EVA respect during this analysis?",
                question_type: "priority",
                why_asked:
                  "Ensures recommendations and visualizations align with real-world constraints.",
              },
            ];
            setState((prev) => ({
              ...prev,
              questions: prev.questions.length
                ? prev.questions
                : fastModeQuestions,
            }));

            // Advance to the visualizations results immediately after simulation finishes
            if (
              lastSimulatedPhase === "rg" ||
              lastSimulatedPhase === "adc" ||
              lastSimulatedPhase === "vpe"
            ) {
              setPhase("vpe_results");
            }

            // Also hydrate visualization, dashboard, and report detail slices from the copied GAL
            (async () => {
              try {
                if (state.sessionId) {
                  try {
                    const vizData = await api.getVisualizations(
                      state.sessionId,
                    );
                    setState((prev) => ({
                      ...prev,
                      visualizationsData: vizData,
                    }));
                  } catch {
                    /* ignore */
                  }

                  try {
                    const dashData = await api.getDashboard(state.sessionId);
                    setState((prev) => ({ ...prev, dashboardData: dashData }));
                  } catch {
                    /* ignore */
                  }

                  try {
                    const repData = await api.getReport(state.sessionId);
                    setState((prev) => ({ ...prev, reportData: repData }));
                  } catch {
                    /* ignore */
                  }
                }
              } catch {
                // silent fail; detailed views will just call their own endpoints later
              }
            })();
          }
        },
      );
    } catch (err: unknown) {
      addLog(
        "SYSTEM",
        `Quick Mode failed: ${err instanceof Error ? err.message : String(err)}`,
        "error",
      );
    } finally {
      setExecuting(false);
    }
  }, [state.sessionId, state.sourceSessionId, addLog, setPhase, setExecuting]);

  return (
    <SessionContext.Provider
      value={{
        ...state,
        addLog,
        createAndUpload,
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
        resetSession,
        getNextAgentName,
        setRulesMode,
        setQuickModeEnabled,
        loadSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}
