"use client";

import { memo } from "react";
import { motion } from "framer-motion";
import { Settings } from "lucide-react";

function ChatHeaderBase() {
    return (
        <motion.div
            className="flex items-center justify-between px-7 py-5"
            style={{
                borderBottom: "1px solid rgba(255,255,255,0.04)",
                /* Subtle bottom-edge luminance */
                boxShadow: "inset 0 -1px 0 rgba(255,255,255,0.02)",
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
        >
            {/* Left — Status + Title */}
            <div className="flex items-center gap-3">
                {/* Status indicator — controlled diffusion, not neon */}
                <div className="relative flex items-center justify-center">
                    <div
                        className="h-1.5 w-1.5 rounded-full"
                        style={{ background: "rgba(34,211,238,0.7)" }}
                    />
                    <motion.div
                        className="absolute h-1.5 w-1.5 rounded-full"
                        style={{ background: "rgba(34,211,238,0.3)" }}
                        animate={{ opacity: [0.4, 0.8, 0.4] }}
                        transition={{
                            duration: 3,
                            repeat: Infinity,
                            ease: "easeInOut",
                        }}
                    />
                </div>
                <h1
                    className="text-[13px] font-medium"
                    style={{
                        color: "rgba(255,255,255,0.7)",
                        letterSpacing: "-0.01em",
                        fontFeatureSettings: '"ss01", "ss02"',
                    }}
                >
                    EVA Research Terminal
                </h1>
            </div>

            {/* Right — Settings ghost button */}
            <button
                className="flex h-8 w-8 items-center justify-center rounded-full transition-all duration-300"
                style={{
                    background: "rgba(255,255,255,0.025)",
                    border: "1px solid rgba(255,255,255,0.04)",
                }}
                onMouseEnter={(e) => {
                    const el = e.currentTarget as HTMLButtonElement;
                    el.style.boxShadow = "0 0 16px rgba(34,211,238,0.12)";
                    el.style.borderColor = "rgba(34,211,238,0.12)";
                }}
                onMouseLeave={(e) => {
                    const el = e.currentTarget as HTMLButtonElement;
                    el.style.boxShadow = "none";
                    el.style.borderColor = "rgba(255,255,255,0.04)";
                }}
                aria-label="Settings"
            >
                <Settings size={13} style={{ color: "rgba(255,255,255,0.35)" }} />
            </button>
        </motion.div>
    );
}

export const ChatHeader = memo(ChatHeaderBase);
