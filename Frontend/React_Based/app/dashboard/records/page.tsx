"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Archive,
  BarChart2,
  LayoutDashboard,
  FileText,
  Search,
  Clock,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { VisualizationGallery } from "@/components/pipeline/VisualizationGallery";
import { KPIDashboard } from "@/components/pipeline/KPIDashboard";
import { ReportView } from "@/components/pipeline/ReportView";

const MONO_FONT = {
  fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
};

interface SessionInfo {
  session_id: string;
  has_visualizations: boolean;
  has_dashboard: boolean;
  has_report: boolean;
  // Fallbacks if available
  timestamp?: string;
  name?: string;
}

export default function RecordsPage() {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetchCompletedSessions();
  }, []);

  const fetchCompletedSessions = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/session/list");
      if (res.ok) {
        const data = await res.json();
        // Filter only fully run sessions (all 9 levels completed generally means these three flags are true)
        const completed = data.filter(
          (s: SessionInfo) =>
            s.has_visualizations && s.has_dashboard && s.has_report,
        );
        setSessions(completed);
      }
    } catch (err) {
      console.error("Failed to fetch sessions for records", err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredSessions = sessions.filter((s) =>
    (s.name || s.session_id).toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="flex h-[calc(100vh-theme(spacing.16))] w-full bg-black/95 text-white overflow-hidden border border-white/10 rounded-xl max-w-[1600px] mx-auto my-4">
      {/* Sidebar for Sessions */}
      <div className="w-80 flex flex-col border-r border-white/10 bg-black/60 backdrop-blur-sm h-full shrink-0">
        <div className="p-4 border-b border-white/10 bg-white/[0.02]">
          <h2
            className="text-lg font-bold text-white flex items-center gap-2 mb-4 tracking-widest uppercase"
            style={MONO_FONT}
          >
            <Archive className="w-5 h-5" />
            Records
          </h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
            <input
              type="text"
              placeholder="Search complete sessions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg py-2 pl-9 pr-4 text-sm text-white placeholder:text-white/30 focus:outline-none focus:border-[#F97316]/50 transition-colors"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center p-8 text-white/40">
              <Loader2 className="w-6 h-6 animate-spin mb-2" />
              <span className="text-sm font-mono" style={MONO_FONT}>
                Loading Records...
              </span>
            </div>
          ) : filteredSessions.length === 0 ? (
            <div
              className="p-4 text-center text-sm text-white/40 font-mono"
              style={MONO_FONT}
            >
              No fully completed sessions found. (All 9 levels must be run).
            </div>
          ) : (
            filteredSessions.map((session) => (
              <motion.button
                key={session.session_id}
                onClick={() => setSelectedSessionId(session.session_id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`w-full text-left p-4 rounded-xl transition-all duration-200 ${
                  selectedSessionId === session.session_id
                    ? "bg-[#F97316]/10 border border-[#F97316]/30 shadow-[0_0_15px_rgba(249,115,22,0.1)]"
                    : "bg-white/[0.02] border border-white/5 hover:bg-white/[0.04]"
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3
                    className="text-emerald-400 font-mono text-sm truncate pr-2"
                    style={MONO_FONT}
                  >
                    {session.name ||
                      `Session ${session.session_id.slice(0, 8)}`}
                  </h3>
                </div>
                <div className="flex flex-wrap gap-1 mb-3">
                  <span className="text-[9px] uppercase px-1.5 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                    Viz
                  </span>
                  <span className="text-[9px] uppercase px-1.5 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                    Dash
                  </span>
                  <span className="text-[9px] uppercase px-1.5 py-0.5 rounded border border-emerald-500/30 text-emerald-400 bg-emerald-500/10">
                    Report
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[10px] text-white/30 font-mono tracking-wider">
                  <div className="flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    <span>{session.session_id.slice(0, 8)}</span>
                  </div>
                </div>
              </motion.button>
            ))
          )}
        </div>
      </div>

      {/* Main Window */}
      <div className="flex-1 flex flex-col relative bg-black/40 shadow-inner overflow-hidden">
        <AnimatePresence mode="wait">
          {!selectedSessionId ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex-1 flex flex-col items-center justify-center text-white/40 space-y-4 p-8 text-center"
            >
              <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                <Archive className="w-8 h-8 opacity-50" />
              </div>
              <h2 className="text-xl font-medium text-white/60 font-mono tracking-wider">
                Select a Record
              </h2>
              <p className="text-sm max-w-md">
                Choose a fully completed pipeline session from the sidebar to
                review its Visualizations, Dashboard, and Narrative Report.
              </p>
            </motion.div>
          ) : (
            <motion.div
              key={selectedSessionId}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="w-full h-full flex flex-col"
            >
              <RecordDetailsWindow sessionId={selectedSessionId} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function RecordDetailsWindow({ sessionId }: { sessionId: string }) {
  const [data, setData] = useState<any>({
    viz: null,
    dash: null,
    report: null,
    loading: true,
    error: false,
  });

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      setData((prev: any) => ({ ...prev, loading: true, error: false }));
      try {
        const [vizRes, dashRes, reportRes] = await Promise.all([
          fetch(`http://localhost:8000/session/${sessionId}/visualizations`),
          fetch(`http://localhost:8000/session/${sessionId}/dashboard`),
          fetch(`http://localhost:8000/session/${sessionId}/report`),
        ]);

        if (isMounted) {
          setData({
            viz: vizRes.ok ? await vizRes.json() : null,
            dash: dashRes.ok ? await dashRes.json() : null,
            report: reportRes.ok ? await reportRes.json() : null,
            loading: false,
            error: false,
          });
        }
      } catch (err) {
        console.error("Failed to fetch record details", err);
        if (isMounted) {
          setData((prev: any) => ({ ...prev, loading: false, error: true }));
        }
      }
    };
    fetchData();
    return () => {
      isMounted = false;
    };
  }, [sessionId]);

  if (data.loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-[#F97316]" />
      </div>
    );
  }

  if (data.error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-red-400 gap-4">
        <AlertCircle className="w-10 h-10" />
        <p>Failed to load session records. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <Tabs defaultValue="visualizations" className="w-full">
          <div className="sticky top-0 z-10 bg-black/90 backdrop-blur pb-4 pt-2 border-b border-white/10 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white tracking-widest uppercase font-mono">
                Record View
              </h3>
              <span className="text-xs text-white/40 font-mono bg-white/5 py-1 px-3 rounded-full border border-white/10">
                {sessionId}
              </span>
            </div>

            <TabsList className="bg-white/[0.02] border border-white/[0.05] p-1 h-auto rounded-xl inline-flex w-full md:w-auto overflow-x-auto">
              {data.viz && (
                <TabsTrigger
                  value="visualizations"
                  className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
                >
                  <BarChart2 className="w-4 h-4" />
                  Visualizations
                </TabsTrigger>
              )}
              {data.dash && (
                <TabsTrigger
                  value="dashboard"
                  className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </TabsTrigger>
              )}
              {data.report && (
                <TabsTrigger
                  value="report"
                  className="rounded-lg px-4 py-2 text-sm font-medium data-[state=active]:bg-white/[0.08] data-[state=active]:text-white text-white/60 flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  Report
                </TabsTrigger>
              )}
            </TabsList>
          </div>

          <TabsContent
            value="visualizations"
            className="mt-0 focus-visible:outline-none focus-visible:ring-0"
          >
            {data.viz?.visualizations?.length > 0 ? (
              <VisualizationGallery
                visualizations={data.viz.visualizations}
                totalRendered={data.viz.total_rendered}
                totalFailed={data.viz.total_failed}
                overallReasoning={data.viz.overall_reasoning}
                onNext={() => {}} // Disabled next in review mode
              />
            ) : (
              <div className="p-8 text-center text-white/40 border border-white/5 rounded-xl bg-white/[0.02]">
                No visualizations found for this record.
              </div>
            )}
          </TabsContent>

          <TabsContent
            value="dashboard"
            className="mt-0 focus-visible:outline-none focus-visible:ring-0"
          >
            {data.dash && data.dash.kpis ? (
              <KPIDashboard
                kpis={data.dash.kpis}
                alerts={data.dash.alerts}
                recommendations={data.dash.recommendations}
                panels={data.dash.panels}
                overallReasoning={data.dash.overall_reasoning}
                onNext={() => {}} // Disabled next in review mode
              />
            ) : (
              <div className="p-8 text-center text-white/40 border border-white/5 rounded-xl bg-white/[0.02]">
                No dashboard components found for this record.
              </div>
            )}
          </TabsContent>

          <TabsContent
            value="report"
            className="mt-0 focus-visible:outline-none focus-visible:ring-0"
          >
            {data.report && data.report.narrative ? (
              <ReportView
                narrative={data.report.narrative}
                citations={data.report.citations}
                communicatedRecommendations={
                  data.report.communicated_recommendations
                }
                stakeholderCalibration={data.report.stakeholder_calibration}
                onNext={() => {}} // Disabled next in review mode
              />
            ) : (
              <div className="p-8 text-center text-white/40 border border-white/5 rounded-xl bg-white/[0.02]">
                No report data found for this record.
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
