"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChatSidebar } from "@/components/chat/Sidebar";
import { ChatWindow } from "@/components/chat/ChatWindow";

export default function ChatDashboardPage() {
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(
    null,
  );

  return (
    <div className="flex h-[calc(100vh-theme(spacing.16))] w-full bg-black/95 text-white overflow-hidden border border-white/10 rounded-xl max-w-[1600px] mx-auto my-4">
      {/* Sidebar for fetching/listing sessions */}
      <ChatSidebar
        selectedSessionId={selectedSessionId}
        onSelectSession={setSelectedSessionId}
      />

      {/* Main chat window */}
      <div className="flex-1 flex flex-col relative bg-black/40 shadow-inner">
        <AnimatePresence mode="wait">
          {!selectedSessionId ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex-1 flex flex-col items-center justify-center text-white/40 space-y-4"
            >
              <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                <svg
                  className="w-8 h-8 opacity-50"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h2 className="text-xl font-medium text-white/60 font-mono tracking-wider">
                Select a Session
              </h2>
              <p className="text-sm max-w-md text-center">
                Choose a past GAL or session from the sidebar to load its
                context and start interrogating your data insights.
              </p>
            </motion.div>
          ) : (
            <motion.div
              key={selectedSessionId}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="w-full h-full"
            >
              <ChatWindow sessionId={selectedSessionId} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
