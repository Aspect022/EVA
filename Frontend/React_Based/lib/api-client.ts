const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// --- Response Types (mirroring Backend Pydantic models) ---

export interface SessionResponse {
  session_id: string
  message: string
}

export interface SessionInfo {
  session_id: string
  has_identity: boolean
  has_intent: boolean
  has_integrity: boolean
  has_findings: boolean
  has_hypotheses: boolean
  has_features: boolean
  has_mlrl: boolean
  has_visualizations: boolean
  has_dashboard: boolean
  has_report: boolean
  csv_file: string | null
  has_lom_data: boolean
  has_lom_profile: boolean
  has_lom_timeline: boolean
  has_lom_rca: boolean
  has_lom_report: boolean
  lom_file_count: number
}

export interface UploadResponse {
  filename: string
  status: string
  session_id: string
}

export interface Phase1aResponse {
  session_id: string
  status: string
  error?: string | null
  questions: Array<Record<string, unknown>>
}

export interface IntentResponse {
  session_id: string
  status: string
  error?: string | null
  primary_objective?: string | null
  selected_target?: string | null
}

export interface ExecuteResponse {
  session_id: string
  status: string
  error?: string | null
}

export interface Phase2Response {
  session_id: string
  status: string
  error?: string | null
  hypotheses_count: number
  hypotheses: Array<Record<string, unknown>>
}

export interface FIEResponse {
  session_id: string
  status: string
  error?: string | null
  features_count: number
  features: Array<Record<string, unknown>>
}

export interface MLRLResponse {
  session_id: string
  status: string
  error?: string | null
  ml: Record<string, unknown>
}

export interface VPEResponse {
  session_id: string
  status: string
  error?: string | null
  visualizations_count: number
  visualizations_failed: number
  visualizations: Array<Record<string, unknown>>
}

export interface ADCResponse {
  session_id: string
  status: string
  error?: string | null
  panels: number
  kpis: number
  alerts: number
  recommendations: number
}

export interface RGResponse {
  session_id: string
  status: string
  error?: string | null
  report: Record<string, unknown>
}

// --- LOM Response Types ---

export interface UploadLomResponse {
  session_id: string
  total_uploaded: number
  uploaded: Array<Record<string, unknown>>
  errors: string[]
}

export interface LOMProfileResponse {
  session_id: string
  status: string
  error?: string | null
  source_inventory: Record<string, unknown>
}

export interface LOMTimelineResponse {
  session_id: string
  status: string
  error?: string | null
  timeline_events: number
  anomalies_found: number
  hypotheses_count: number
  hypotheses: Array<Record<string, unknown>>
}

export interface LOMReportResponse {
  session_id: string
  status: string
  error?: string | null
  report: Record<string, unknown>
}

export interface LOMGalData {
  session_id: string
  source_inventory?: Record<string, unknown>
  log_profile?: Record<string, unknown>
  metric_profile?: Record<string, unknown>
  timeline?: Record<string, unknown>
  rca_hypotheses?: Record<string, unknown>
  rca_report?: Record<string, unknown>
  [key: string]: unknown
}

export interface CheckDatasetResponse {
  quick_mode_available: boolean
  source_session_id: string | null
  completed_phases: string[]
}

export interface QuickModeEvent {
  type: "log" | "phase_result" | "done"
  agent?: string
  message?: string
  log_type?: string
  phase?: string
  [key: string]: unknown
}

export interface VisualizationsData {
  visualizations: Array<Record<string, unknown>>
  total_rendered: number
  total_failed: number
  total_planned: number
  overall_reasoning: string
}

export interface DashboardData {
  kpis: Array<Record<string, unknown>>
  alerts: Array<Record<string, unknown>>
  recommendations: Array<Record<string, unknown>>
  panels: Array<Record<string, unknown>>
  stakeholder_calibration: string
  overall_reasoning: string
}

export interface ReportData {
  narrative: string
  citations: string[]
  included_visualizations: string[]
  communicated_recommendations: string[]
  stakeholder_calibration: string
}

// --- API Functions ---

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 600_000) // 10 min timeout

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...options?.headers },
    })
    if (!res.ok) {
      const detail = await res.text().catch(() => res.statusText)
      throw new Error(`API ${res.status}: ${detail}`)
    }
    const data = await res.json()
    if (data && typeof data === "object" && "error" in data && data.error) {
      throw new Error(data.error as string)
    }
    return data as T
  } finally {
    clearTimeout(timeout)
  }
}

export const api = {
  listSessions: () =>
    apiFetch<SessionInfo[]>("/session/list"),

  createSession: () =>
    apiFetch<SessionResponse>("/session/create", { method: "POST" }),

  uploadDataset: async (sessionId: string, file: File) => {
    const form = new FormData()
    form.append("file", file)
    const res = await fetch(`${API_BASE}/session/${sessionId}/upload`, {
      method: "POST",
      body: form,
    })
    if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`)
    return res.json() as Promise<UploadResponse>
  },

  executePhase1a: (sessionId: string, csvFileName: string, rulesMode = "full") =>
    apiFetch<Phase1aResponse>(
      `/session/${sessionId}/execute/phase1a?csv_file_name=${encodeURIComponent(csvFileName)}&rules_mode=${rulesMode}`,
      { method: "POST" }
    ),

  submitAnswers: (sessionId: string, answers: Record<string, string>, rulesMode = "full") =>
    apiFetch<IntentResponse>(
      `/session/${sessionId}/submit-answers?rules_mode=${rulesMode}`,
      { method: "POST", body: JSON.stringify({ answers }) }
    ),

  executePhase1b: (sessionId: string, csvFileName: string, rulesMode = "full") =>
    apiFetch<ExecuteResponse>(
      `/session/${sessionId}/execute/phase1b?csv_file_name=${encodeURIComponent(csvFileName)}&rules_mode=${rulesMode}`,
      { method: "POST" }
    ),

  executePhase2: (sessionId: string, rulesMode = "full") =>
    apiFetch<Phase2Response>(
      `/session/${sessionId}/execute/phase2?rules_mode=${rulesMode}`,
      { method: "POST" }
    ),

  executeFIE: (sessionId: string, rulesMode = "full") =>
    apiFetch<FIEResponse>(
      `/session/${sessionId}/execute/fie?rules_mode=${rulesMode}`,
      { method: "POST" }
    ),

  executeMLRL: (sessionId: string, rulesMode = "full") =>
    apiFetch<MLRLResponse>(
      `/session/${sessionId}/execute/mlrl?rules_mode=${rulesMode}`,
      { method: "POST" }
    ),

  executeVPE: (sessionId: string, rulesMode = "full") =>
    apiFetch<VPEResponse>(
      `/session/${sessionId}/execute/vpe?rules_mode=${rulesMode}`,
      { method: "POST" }
    ),

  executeADC: (sessionId: string, rulesMode = "full") =>
    apiFetch<ADCResponse>(
      `/session/${sessionId}/execute/adc?rules_mode=${rulesMode}`,
      { method: "POST" }
    ),

  executeRG: (sessionId: string, rulesMode = "full") =>
    apiFetch<RGResponse>(
      `/session/${sessionId}/execute/rg?rules_mode=${rulesMode}`,
      { method: "POST" }
    ),

  getGAL: (sessionId: string) =>
    apiFetch<Record<string, unknown>>(`/session/${sessionId}/gal`),

  getVisualizations: (sessionId: string) =>
    apiFetch<VisualizationsData>(`/session/${sessionId}/visualizations`),

  getDashboard: (sessionId: string) =>
    apiFetch<DashboardData>(`/session/${sessionId}/dashboard`),

  getReport: (sessionId: string) =>
    apiFetch<ReportData>(`/session/${sessionId}/report`),

  // --- LOM API Functions ---
  
  uploadLomDataset: async (sessionId: string, files: File[]) => {
    const form = new FormData()
    files.forEach(f => form.append("files", f))
    const res = await fetch(`${API_BASE}/session/${sessionId}/upload-lom`, {
      method: "POST",
      body: form,
    })
    if (!res.ok) throw new Error(`LOM Upload failed: ${res.statusText}`)
    return res.json() as Promise<UploadLomResponse>
  },

  executeLomProfile: (sessionId: string) =>
    apiFetch<LOMProfileResponse>(`/session/${sessionId}/execute/lom-profile`, { method: "POST" }),

  executeLomTimeline: (sessionId: string) =>
    apiFetch<LOMTimelineResponse>(`/session/${sessionId}/execute/lom-timeline`, { method: "POST" }),
    
  executeLomReport: (sessionId: string) =>
    apiFetch<LOMReportResponse>(`/session/${sessionId}/execute/lom-report`, { method: "POST" }),

  getLomGal: (sessionId: string) =>
    apiFetch<LOMGalData>(`/session/${sessionId}/lom-gal`),

  checkDataset: (sessionId: string) =>
    apiFetch<CheckDatasetResponse>(
      `/session/${sessionId}/check-dataset`,
      { method: "POST" }
    ),

  streamQuickMode: (sessionId: string, sourceSessionId: string, onEvent: (event: QuickModeEvent) => void): Promise<void> => {
    return new Promise((resolve, reject) => {
      fetch(`${API_BASE}/session/${sessionId}/quick-mode?source_session_id=${encodeURIComponent(sourceSessionId)}`, {
        method: "POST",
      }).then(response => {
        if (!response.ok) {
          reject(new Error(`Quick Mode failed: ${response.statusText}`))
          return
        }
        const reader = response.body?.getReader()
        if (!reader) {
          reject(new Error("No response body"))
          return
        }
        const decoder = new TextDecoder()
        let buffer = ""

        function processChunk(): Promise<void> {
          return reader!.read().then(({ done, value }) => {
            if (done) {
              resolve()
              return
            }
            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split("\n")
            buffer = lines.pop() || ""
            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const parsed = JSON.parse(line.slice(6)) as QuickModeEvent
                  onEvent(parsed)
                } catch { /* skip malformed */ }
              }
            }
            return processChunk()
          })
        }

        processChunk().catch(reject)
      }).catch(reject)
    })
  },
}
