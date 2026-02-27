"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { api, type SessionInfo } from "@/lib/api-client"
import { Clock, FileText, ArrowRight, RefreshCw } from "lucide-react"

export default function SessionsPage() {
  const [sessions, setSessions] = useState<SessionInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const loadSessions = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await api.listSessions()
      setSessions(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load sessions")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadSessions()
  }, [])

  const getProgress = (s: SessionInfo) => {
    const steps = [
      s.has_identity,
      s.has_intent,
      s.has_integrity,
      s.has_findings,
      s.has_hypotheses,
      s.has_features,
      s.has_visualizations,
      s.has_dashboard,
      s.has_report,
    ]
    return steps.filter(Boolean).length
  }

  const getPhaseLabel = (s: SessionInfo) => {
    if (s.has_report) return "Complete"
    if (s.has_dashboard) return "Report Pending"
    if (s.has_visualizations) return "Dashboard Pending"
    if (s.has_features) return "Visualizations Pending"
    if (s.has_hypotheses) return "Features Pending"
    if (s.has_findings) return "Hypotheses Pending"
    if (s.has_integrity) return "Exploration Pending"
    if (s.has_intent) return "Repair Pending"
    if (s.has_identity) return "Questions Pending"
    return "Upload Pending"
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-[var(--alabaster-grey)]">Sessions</h1>
          <p className="text-[var(--dusty-denim)] text-sm mt-1">Previous analysis sessions</p>
        </div>
        <button
          onClick={loadSessions}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[var(--dusk-blue)] text-[var(--dusty-denim)] hover:text-[var(--alabaster-grey)] hover:bg-[var(--prussian-blue)] transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg border border-red-500/30 bg-red-900/10 text-red-400 text-sm">
          {error}
        </div>
      )}

      {isLoading && sessions.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="w-10 h-10 border-4 border-[var(--dusk-blue)] border-t-[var(--dusty-denim)] rounded-full animate-spin" />
          <p className="text-[var(--dusty-denim)] font-mono text-sm">Loading sessions...</p>
        </div>
      ) : sessions.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 space-y-4 border border-[var(--dusk-blue)] rounded-xl bg-[var(--prussian-blue)]/20">
          <Clock className="w-12 h-12 text-[var(--dusk-blue)]" />
          <p className="text-[var(--dusty-denim)]">No sessions found. Start a new analysis from the Pipeline page.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => {
            const progress = getProgress(session)
            const phase = getPhaseLabel(session)

            return (
              <div
                key={session.session_id}
                className="flex items-center justify-between p-5 rounded-xl border border-[var(--dusk-blue)] bg-[var(--prussian-blue)]/20 hover:bg-[var(--prussian-blue)]/40 transition-all group cursor-pointer"
                onClick={() => router.push(`/dashboard?session=${session.session_id}`)}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-[var(--prussian-blue)] border border-[var(--dusk-blue)] flex items-center justify-center">
                    <FileText className="w-5 h-5 text-[var(--dusty-denim)]" />
                  </div>
                  <div>
                    <p className="font-mono text-sm text-[var(--alabaster-grey)]">
                      {session.session_id.slice(0, 12)}...
                    </p>
                    <p className="text-xs text-[var(--dusty-denim)] mt-0.5">
                      {session.csv_file || "No file"} · {phase}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  {/* Progress bar */}
                  <div className="hidden sm:flex items-center gap-1">
                    {Array.from({ length: 9 }).map((_, i) => (
                      <div
                        key={i}
                        className={`w-3 h-1.5 rounded-full transition-colors ${
                          i < progress ? "bg-[var(--dusty-denim)]" : "bg-[var(--dusk-blue)]"
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-xs font-mono text-[var(--dusty-denim)]">{progress}/9</span>
                  <ArrowRight className="w-4 h-4 text-[var(--dusk-blue)] group-hover:text-[var(--alabaster-grey)] transition-colors" />
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
