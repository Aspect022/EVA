"use client";

import { memo } from "react";
import { motion } from "framer-motion";

export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
}

interface ChatMessageProps {
    message: Message;
    index: number;
}

/* ── Intelligent stagger animation ───────────────────── */
const messageVariants = {
    hidden: { opacity: 0, y: 8, filter: "blur(2px)" },
    visible: (i: number) => ({
        opacity: 1,
        y: 0,
        filter: "blur(0px)",
        transition: {
            duration: 0.4,
            ease: [0.25, 0.1, 0.25, 1.0],
            delay: i * 0.08,
        },
    }),
};

/* ── Glass surface styles ────────────────────────────── */
const assistantStyle = {
    maxWidth: "72%",
    background: "rgba(255,255,255,0.02)",
    backdropFilter: "blur(12px)",
    WebkitBackdropFilter: "blur(12px)",
    border: "1px solid rgba(255,255,255,0.04)",
    boxShadow: [
        /* Depth */
        "0 2px 12px rgba(0,0,0,0.15)",
        /* Inner top-edge luminance */
        "inset 0 1px 0 rgba(255,255,255,0.04)",
        /* Ultra-subtle violet diffusion — lab-grade, not neon */
        "inset 0 0 24px rgba(139,92,246,0.025)",
    ].join(", "),
    color: "rgba(255,255,255,0.78)",
};

const userStyle = {
    maxWidth: "72%",
    background: "rgba(255,255,255,0.035)",
    backdropFilter: "blur(8px)",
    WebkitBackdropFilter: "blur(8px)",
    borderLeft: "1.5px solid rgba(34,211,238,0.2)",
    border: "1px solid rgba(255,255,255,0.05)",
    boxShadow: [
        "0 4px 16px rgba(0,0,0,0.2)",
        "inset 0 1px 0 rgba(255,255,255,0.05)",
    ].join(", "),
    color: "rgba(255,255,255,0.85)",
};

function ChatMessageBase({ message, index }: ChatMessageProps) {
    const isUser = message.role === "user";

    return (
        <motion.div
            className={`flex ${isUser ? "justify-end" : "justify-start"} px-6`}
            variants={messageVariants}
            custom={index}
            initial="hidden"
            animate="visible"
        >
            <div
                className="rounded-2xl px-5 py-3.5 text-[13.5px] leading-[1.65]"
                style={isUser ? { ...userStyle, borderLeft: "1.5px solid rgba(34,211,238,0.2)" } : assistantStyle}
            >
                {message.content}
            </div>
        </motion.div>
    );
}

export const ChatMessage = memo(ChatMessageBase);
