"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FileText, Clock, Search, Loader2 } from "lucide-react";

interface SessionInfo {
  session_id: string;
  name: string;
  timestamp: string;
  goal: string;
}

interface ChatSidebarProps {
  selectedSessionId: string | null;
  onSelectSession: (id: string) => void;
}

const MONO_FONT = {
  fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
};

export function ChatSidebar({
  selectedSessionId,
  onSelectSession,
}: ChatSidebarProps) {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/chat/sessions");
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.error("Failed to fetch sessions for chat", err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredSessions = sessions.filter(
    (s) =>
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.goal.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="w-80 flex flex-col border-r border-white/10 bg-black/60 backdrop-blur-sm h-full">
      <div className="p-4 border-b border-white/10">
        <h2
          className="text-lg font-bold text-white tracking-widest uppercase mb-4"
          style={MONO_FONT}
        >
          Chat Contexts
        </h2>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search sessions..."
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
              Loading...
            </span>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div
            className="p-4 text-center text-sm text-white/40 font-mono"
            style={MONO_FONT}
          >
            No sessions found.
          </div>
        ) : (
          filteredSessions.map((session) => (
            <motion.button
              key={session.session_id}
              onClick={() => onSelectSession(session.session_id)}
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
                  {session.name}
                </h3>
              </div>
              <p className="text-xs text-white/60 line-clamp-2 mb-3">
                {session.goal === "Unknown Goal"
                  ? "No goal defined."
                  : session.goal}
              </p>
              <div className="flex items-center gap-3 text-[10px] text-white/30 font-mono tracking-wider">
                <div className="flex items-center gap-1">
                  <FileText className="w-3 h-3" />
                  <span>{session.session_id.slice(0, 8)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{session.timestamp.slice(0, 10)}</span>
                </div>
              </div>
            </motion.button>
          ))
        )}
      </div>
    </div>
  );
}
