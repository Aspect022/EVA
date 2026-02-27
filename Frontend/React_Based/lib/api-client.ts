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
  has_visualizations: boolean
  has_dashboard: boolean
  has_report: boolean
  csv_file: string | null
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
    return res.json()
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
}
