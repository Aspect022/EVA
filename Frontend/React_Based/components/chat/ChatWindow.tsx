"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Send, Bot, User, Loader2 } from "lucide-react";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

interface ChatWindowProps {
  sessionId: string;
}

const MONO_FONT = {
  fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
};

export function ChatWindow({ sessionId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Session context actively loaded. What insights would you like to uncover?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Reset messages when session changes
    setMessages([
      {
        role: "assistant",
        content: `Session limits synchronized: ${sessionId.slice(0, 8)}. Awaiting interrogation parameters.`,
      },
    ]);
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMsg: Message = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      // Send the current message history (excluding the first greeting to save tokens if we want, or keep it)
      const messageHistory = [
        ...messages.filter((m) => m.role !== "system"),
        userMsg,
      ];

      const res = await fetch("http://localhost:8000/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          messages: messageHistory,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.content },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Error: Unable to connect to inference pipeline.",
          },
        ]);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error: Network anomaly during transmission.",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-neutral-900/50 via-black to-black">
      {/* Header */}
      <div className="p-4 border-b border-white/5 flex items-center justify-between bg-black/20 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#F97316]/10 border border-[#F97316]/20 flex items-center justify-center">
            <Bot className="w-5 h-5 text-[#F97316]" />
          </div>
          <div>
            <h3
              className="text-white/90 font-medium font-mono"
              style={MONO_FONT}
            >
              Analysis AI
            </h3>
            <div className="flex items-center gap-2 text-xs text-emerald-400 mt-0.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Conduit Active
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
        {messages.map((msg, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`flex gap-4 max-w-[80%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                  msg.role === "user"
                    ? "bg-white/10"
                    : "bg-[#F97316]/10 border border-[#F97316]/20"
                }`}
              >
                {msg.role === "user" ? (
                  <User className="w-4 h-4 text-white/60" />
                ) : (
                  <Bot className="w-4 h-4 text-[#F97316]" />
                )}
              </div>
              <div
                className={`px-5 py-3.5 rounded-2xl text-[15px] leading-relaxed shadow-sm ${
                  msg.role === "user"
                    ? "bg-white/10 text-white/90 rounded-tr-none"
                    : "bg-black/60 border border-white/5 text-white/80 rounded-tl-none font-mono tracking-wide"
                }`}
                style={msg.role !== "user" ? MONO_FONT : {}}
              >
                {/* Very simplistic markdown rendering just replacing \n with <br/> for now. 
                    A real app would use react-markdown here. */}
                {msg.content.split("\n").map((line, i) => (
                  <span key={i}>
                    {line}
                    <br />
                  </span>
                ))}
              </div>
            </div>
          </motion.div>
        ))}

        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex w-full justify-start"
          >
            <div className="flex gap-4 max-w-[80%] flex-row">
              <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-[#F97316]/10 border border-[#F97316]/20">
                <Bot className="w-4 h-4 text-[#F97316]" />
              </div>
              <div className="px-5 py-3.5 rounded-2xl bg-black/60 border border-white/5 rounded-tl-none flex items-center gap-2">
                <Loader2 className="w-4 h-4 !text-[#F97316] animate-spin" />
                <span
                  className="text-xs text-white/40 font-mono tracking-widest"
                  style={MONO_FONT}
                >
                  COMPUTING...
                </span>
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-black/40 border-t border-white/5 backdrop-blur-xl">
        <div className="relative max-w-4xl mx-auto flex items-end gap-2 p-1 border border-white/10 rounded-2xl bg-white/[0.02] focus-within:bg-white/[0.05] focus-within:border-[#F97316]/30 transition-all duration-300">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your query... (Shift+Enter for new line)"
            className="flex-1 max-h-48 min-h-[44px] bg-transparent resize-none p-3 text-[15px] text-white/90 placeholder:text-white/30 focus:outline-none custom-scrollbar"
            rows={1}
            style={{ minHeight: "44px" }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className={`p-3 rounded-xl mb-1 mr-1 transition-all duration-200 flex items-center justify-center ${
              !input.trim() || isTyping
                ? "bg-white/5 text-white/20"
                : "bg-[#F97316] hover:bg-[#F97316]/90 text-white shadow-[0_0_15px_rgba(249,115,22,0.4)]"
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="text-center mt-2">
          <span
            className="text-[10px] text-white/20 font-mono uppercase tracking-[0.2em]"
            style={MONO_FONT}
          >
            AI Models Can Fabricate Insights. Verify Findings.
          </span>
        </div>
      </div>
    </div>
  );
}
