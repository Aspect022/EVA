"use client"

import { createContext, useContext, useState, useCallback, type ReactNode } from "react"
import { api, type QuickModeEvent, type VisualizationsData, type DashboardData, type ReportData } from "./api-client"

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
  { id: "complete", label: "Complete", agent: "—" },
] as const

export type PhaseId = (typeof PIPELINE_PHASES)[number]["id"]

export interface LogEntry {
  timestamp: string
  agent: string
  message: string
  type: "info" | "success" | "warn" | "error"
}

export type RulesMode = "full" | "lite"

interface SessionState {
  sessionId: string | null
  csvFileName: string | null
  currentPhase: PhaseId
  isExecuting: boolean
  rulesMode: RulesMode
  logs: LogEntry[]
  // Quick Mode
  quickModeAvailable: boolean
  quickModeEnabled: boolean
  sourceSessionId: string | null
  completedPhases: string[]
  // Phase-specific results
  questions: Array<Record<string, unknown>>
  intent: { primary_objective?: string; selected_target?: string } | null
  hypotheses: Array<Record<string, unknown>>
  features: Array<Record<string, unknown>>
  visualizations: Array<Record<string, unknown>>
  visualizationsData: VisualizationsData | null
  dashboardStats: { panels: number; kpis: number; alerts: number; recommendations: number } | null
  dashboardData: DashboardData | null
  report: Record<string, unknown> | null
  reportData: ReportData | null
}

interface SessionContextType extends SessionState {
  addLog: (agent: string, message: string, type: LogEntry["type"]) => void
  createAndUpload: (file: File) => Promise<void>
  runPhase1a: () => Promise<void>
  submitUserAnswers: (answers: Record<string, string>) => Promise<void>
  runPhase1b: () => Promise<void>
  runPhase2: () => Promise<void>
  runFIE: () => Promise<void>
  runVPE: () => Promise<void>
  runADC: () => Promise<void>
  runRG: () => Promise<void>
  runQuickMode: () => Promise<void>
  advanceFromResults: () => void
  resetSession: () => void
  getNextAgentName: () => string
  setRulesMode: (mode: RulesMode) => void
  setQuickModeEnabled: (enabled: boolean) => void
}

const SessionContext = createContext<SessionContextType | null>(null)

export function useSession() {
  const ctx = useContext(SessionContext)
  if (!ctx) throw new Error("useSession must be used within SessionProvider")
  return ctx
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
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SessionState>(initialState)

  const addLog = useCallback((agent: string, message: string, type: LogEntry["type"]) => {
    setState(prev => ({
      ...prev,
      logs: [...prev.logs, { timestamp: new Date().toLocaleTimeString(), agent, message, type }],
    }))
  }, [])

  const setPhase = useCallback((phase: PhaseId) => {
    setState(prev => ({ ...prev, currentPhase: phase }))
  }, [])

  const setExecuting = useCallback((v: boolean) => {
    setState(prev => ({ ...prev, isExecuting: v }))
  }, [])

  const createAndUpload = useCallback(async (file: File) => {
    setExecuting(true)
    try {
      addLog("SYSTEM", "Creating session...", "info")
      const session = await api.createSession()
      setState(prev => ({ ...prev, sessionId: session.session_id }))
      addLog("SYSTEM", `Session ${session.session_id.slice(0, 8)}... created`, "success")

      addLog("SYSTEM", `Uploading ${file.name}...`, "info")
      const upload = await api.uploadDataset(session.session_id, file)
      setState(prev => ({ ...prev, csvFileName: upload.filename }))
      addLog("SYSTEM", `File "${upload.filename}" uploaded successfully`, "success")

      // Check if this dataset was previously analyzed (Quick Mode)
      try {
        const check = await api.checkDataset(session.session_id)
        if (check.quick_mode_available) {
          setState(prev => ({
            ...prev,
            quickModeAvailable: true,
            sourceSessionId: check.source_session_id,
            completedPhases: check.completed_phases,
          }))
          addLog("SYSTEM", "Cached analysis detected — Quick Mode available", "info")
        }
      } catch { /* silently skip if check fails */ }

      setPhase("phase1a")
    } catch (err: unknown) {
      addLog("SYSTEM", `Upload failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [addLog, setPhase, setExecuting])

  const runPhase1a = useCallback(async () => {
    if (!state.sessionId || !state.csvFileName) return
    setExecuting(true)
    try {
      addLog("DPSU", "Running dataset profiling...", "info")
      addLog("QBII", "Generating targeted questions...", "info")
      const res = await api.executePhase1a(state.sessionId, state.csvFileName, state.rulesMode)
      setState(prev => ({ ...prev, questions: res.questions }))
      addLog("QBII", `Generated ${res.questions.length} question(s)`, "success")
      setPhase("answers")
    } catch (err: unknown) {
      addLog("DPSU", `Phase 1a failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, state.csvFileName, addLog, setPhase, setExecuting])

  const submitUserAnswers = useCallback(async (answers: Record<string, string>) => {
    if (!state.sessionId) return
    setExecuting(true)
    try {
      addLog("QBII", "Processing user intent...", "info")
      const res = await api.submitAnswers(state.sessionId, answers, state.rulesMode)
      setState(prev => ({
        ...prev,
        intent: { primary_objective: res.primary_objective ?? undefined, selected_target: res.selected_target ?? undefined },
      }))
      addLog("QBII", `Intent confirmed: ${res.primary_objective}`, "success")
      setPhase("phase1b")
    } catch (err: unknown) {
      addLog("QBII", `Answer submission failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, addLog, setPhase, setExecuting])

  const runPhase1b = useCallback(async () => {
    if (!state.sessionId || !state.csvFileName) return
    setExecuting(true)
    try {
      addLog("DRIL", "Running data repair & integrity checks...", "info")
      addLog("EPR", "Running exploratory analysis...", "info")
      await api.executePhase1b(state.sessionId, state.csvFileName, state.rulesMode)
      addLog("EPR", "Exploration complete", "success")
      setPhase("phase2")
    } catch (err: unknown) {
      addLog("DRIL", `Phase 1b failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, state.csvFileName, addLog, setPhase, setExecuting])

  const runPhase2 = useCallback(async () => {
    if (!state.sessionId) return
    setExecuting(true)
    try {
      addLog("IHE", "Generating hypotheses from findings...", "info")
      const res = await api.executePhase2(state.sessionId, state.rulesMode)
      setState(prev => ({ ...prev, hypotheses: res.hypotheses }))
      addLog("IHE", `Generated ${res.hypotheses_count} hypothesis(es)`, "success")
      setPhase("fie")
    } catch (err: unknown) {
      addLog("IHE", `Phase 2 failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, addLog, setPhase, setExecuting])

  const runFIE = useCallback(async () => {
    if (!state.sessionId) return
    setExecuting(true)
    try {
      addLog("FIE", "Running feature intelligence engine...", "info")
      const res = await api.executeFIE(state.sessionId, state.rulesMode)
      setState(prev => ({ ...prev, features: res.features }))
      addLog("FIE", `Engineered ${res.features_count} feature(s)`, "success")
      setPhase("vpe")
    } catch (err: unknown) {
      addLog("FIE", `FIE failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, addLog, setPhase, setExecuting])

  const runVPE = useCallback(async () => {
    if (!state.sessionId) return
    setExecuting(true)
    try {
      addLog("VPE", "Planning and generating visualizations...", "info")
      const res = await api.executeVPE(state.sessionId, state.rulesMode)
      setState(prev => ({ ...prev, visualizations: res.visualizations }))
      addLog("VPE", `Created ${res.visualizations_count} visualization(s)`, "success")

      // Fetch full visualization data with plotly_config
      try {
        const vizData = await api.getVisualizations(state.sessionId)
        setState(prev => ({ ...prev, visualizationsData: vizData }))
      } catch { /* fallback: show results without charts */ }

      setPhase("vpe_results")
    } catch (err: unknown) {
      addLog("VPE", `VPE failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, addLog, setPhase, setExecuting])

  const runADC = useCallback(async () => {
    if (!state.sessionId) return
    setExecuting(true)
    try {
      addLog("ADC", "Composing analytical dashboard...", "info")
      const res = await api.executeADC(state.sessionId, state.rulesMode)
      setState(prev => ({
        ...prev,
        dashboardStats: { panels: res.panels, kpis: res.kpis, alerts: res.alerts, recommendations: res.recommendations },
      }))
      addLog("ADC", `Dashboard ready: ${res.panels} panels, ${res.kpis} KPIs`, "success")

      // Fetch full dashboard data with content
      try {
        const dashData = await api.getDashboard(state.sessionId)
        setState(prev => ({ ...prev, dashboardData: dashData }))
      } catch { /* fallback: show summary only */ }

      setPhase("adc_results")
    } catch (err: unknown) {
      addLog("ADC", `ADC failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, addLog, setPhase, setExecuting])

  const runRG = useCallback(async () => {
    if (!state.sessionId) return
    setExecuting(true)
    try {
      addLog("RG", "Generating final report...", "info")
      const res = await api.executeRG(state.sessionId, state.rulesMode)
      setState(prev => ({ ...prev, report: res.report }))
      addLog("RG", "Report generated successfully", "success")

      // Fetch full report data
      try {
        const reportData = await api.getReport(state.sessionId)
        setState(prev => ({ ...prev, reportData }))
      } catch { /* fallback */ }

      setPhase("rg_results")
    } catch (err: unknown) {
      addLog("RG", `Report generation failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, addLog, setPhase, setExecuting])

  const resetSession = useCallback(() => {
    setState(initialState)
  }, [])

  const advanceFromResults = useCallback(() => {
    if (state.currentPhase === "vpe_results") setPhase("adc")
    else if (state.currentPhase === "adc_results") setPhase("rg")
    else if (state.currentPhase === "rg_results") setPhase("complete")
  }, [state.currentPhase, setPhase])

  const getNextAgentName = useCallback(() => {
    const idx = PIPELINE_PHASES.findIndex(p => p.id === state.currentPhase)
    if (idx < 0 || idx >= PIPELINE_PHASES.length) return "—"
    return PIPELINE_PHASES[idx].agent
  }, [state.currentPhase])

  const setRulesMode = useCallback((mode: RulesMode) => {
    setState(prev => ({ ...prev, rulesMode: mode }))
  }, [])

  const setQuickModeEnabled = useCallback((enabled: boolean) => {
    setState(prev => ({ ...prev, quickModeEnabled: enabled }))
  }, [])

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
  }

  const runQuickMode = useCallback(async () => {
    if (!state.sessionId || !state.sourceSessionId) return
    setExecuting(true)
    try {
      addLog("SYSTEM", "Quick Mode activated — replaying cached analysis...", "info")
      await api.streamQuickMode(state.sessionId, state.sourceSessionId, (event: QuickModeEvent) => {
        if (event.type === "log") {
          const logType = (event.log_type === "success" || event.log_type === "error" || event.log_type === "warn" || event.log_type === "info")
            ? event.log_type as LogEntry["type"]
            : "info"
          addLog(event.agent || "SYSTEM", event.message || "", logType)
        } else if (event.type === "phase_result" && event.phase) {
          const phase = event.phase as string
          // Update state based on which phase completed
          if (phase === "phase1a" && event.questions) {
            setState(prev => ({ ...prev, questions: event.questions as Array<Record<string, unknown>> }))
          } else if (phase === "answers") {
            setState(prev => ({
              ...prev,
              intent: {
                primary_objective: event.primary_objective as string | undefined,
                selected_target: event.selected_target as string | undefined,
              },
            }))
          } else if (phase === "phase2" && event.hypotheses) {
            setState(prev => ({ ...prev, hypotheses: event.hypotheses as Array<Record<string, unknown>> }))
          } else if (phase === "fie" && event.features) {
            setState(prev => ({ ...prev, features: event.features as Array<Record<string, unknown>> }))
          } else if (phase === "vpe" && event.visualizations) {
            setState(prev => ({ ...prev, visualizations: event.visualizations as Array<Record<string, unknown>> }))
          } else if (phase === "adc") {
            setState(prev => ({
              ...prev,
              dashboardStats: {
                panels: (event.panels as number) || 0,
                kpis: (event.kpis as number) || 0,
                alerts: (event.alerts as number) || 0,
                recommendations: (event.recommendations as number) || 0,
              },
            }))
          } else if (phase === "rg" && event.report) {
            setState(prev => ({ ...prev, report: event.report as Record<string, unknown> }))
          }
          // Advance to the next phase
          const nextPhase = PHASE_MAP[phase]
          if (nextPhase) setPhase(nextPhase)
        } else if (event.type === "done") {
          addLog("SYSTEM", "Quick Mode complete — all phases simulated", "success")
        }
      })
    } catch (err: unknown) {
      addLog("SYSTEM", `Quick Mode failed: ${err instanceof Error ? err.message : String(err)}`, "error")
    } finally {
      setExecuting(false)
    }
  }, [state.sessionId, state.sourceSessionId, addLog, setPhase, setExecuting])

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
        runVPE,
        runADC,
        runRG,
        runQuickMode,
        advanceFromResults,
        resetSession,
        getNextAgentName,
        setRulesMode,
        setQuickModeEnabled,
      }}
    >
      {children}
    </SessionContext.Provider>
  )
}
