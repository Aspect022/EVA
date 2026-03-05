"use client";

import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { ChatPanel } from "@/components/eva-chat/ChatPanel";
import { ChatHeader } from "@/components/eva-chat/ChatHeader";
import { ChatMessage, type Message } from "@/components/eva-chat/ChatMessage";
import { ChatInput } from "@/components/eva-chat/ChatInput";
import { TypingIndicator } from "@/components/eva-chat/TypingIndicator";

/* ── Sample data ────────────────────────────────────── */
const INITIAL_MESSAGES: Message[] = [
    {
        id: "1",
        role: "assistant",
        content:
            "Welcome to the EVA Research Terminal. I'm ready to assist with data analysis, model evaluation, and research workflows. How can I help you today?",
    },
    {
        id: "2",
        role: "user",
        content:
            "Can you run a comparative analysis on the latest transformer architectures? Focus on efficiency metrics.",
    },
    {
        id: "3",
        role: "assistant",
        content:
            "I'll analyze the latest transformer variants — including Mamba, RWKV-6, and Griffin — across FLOPs, throughput, and memory footprint. Give me a moment to compile the benchmarks.",
    },
    {
        id: "4",
        role: "user",
        content: "Also include latency per token at batch size 1 on A100.",
    },
    {
        id: "5",
        role: "assistant",
        content:
            "Noted. I'll add single-batch A100 latency to the comparison matrix. The analysis will cover 7 architectures across 4 parameter scales. Results will be formatted as an interactive table with sortable columns.",
    },
];

/* ── Assistant mock responses ───────────────────────── */
const MOCK_RESPONSES = [
    "I've processed your request. The analysis pipeline is configured and ready. Shall I proceed with the full evaluation?",
    "Interesting approach. Let me cross-reference that against the latest benchmark data from the research corpus.",
    "The results are ready. I've identified three key patterns in the data that warrant further investigation.",
    "Running the computation now. Initial estimates suggest a 23% improvement over the baseline configuration.",
    "I've compiled the findings into a structured report. The key insight is the non-linear scaling behavior observed at the 7B parameter threshold.",
];

/* ── Grid pattern SVG (research terminal atmosphere) ── */
const GRID_SVG = `data:image/svg+xml,${encodeURIComponent(
    `<svg width="60" height="60" xmlns="http://www.w3.org/2000/svg">
    <path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="0.5"/>
  </svg>`
)}`;

export default function EvaChatPage() {
    const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
    const [isTyping, setIsTyping] = useState(false);
    const [tilt, setTilt] = useState({ x: 0, y: 0 });
    const [isMobile, setIsMobile] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const responseIndex = useRef(0);
    const rafRef = useRef<number>(0);

    /* ── Mobile check ──────────────────────────────────── */
    useEffect(() => {
        const check = () => setIsMobile(window.innerWidth < 768);
        check();
        window.addEventListener("resize", check);
        return () => window.removeEventListener("resize", check);
    }, []);

    /* ── Auto-scroll ───────────────────────────────────── */
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isTyping]);

    /* ── 3D tilt — throttled via RAF for performance ──── */
    const handleMouseMove = useCallback(
        (e: React.MouseEvent<HTMLDivElement>) => {
            if (isMobile) return;
            const rect = e.currentTarget.getBoundingClientRect();
            const clientX = e.clientX;
            const clientY = e.clientY;
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
            rafRef.current = requestAnimationFrame(() => {
                const cx = rect.left + rect.width / 2;
                const cy = rect.top + rect.height / 2;
                const dx = (clientX - cx) / (rect.width / 2);
                const dy = (clientY - cy) / (rect.height / 2);
                /* Max ±1.5deg — extremely restrained */
                setTilt({ x: dy * -1.5, y: dx * 1.5 });
            });
        },
        [isMobile]
    );

    const handleMouseLeave = useCallback(() => {
        if (rafRef.current) cancelAnimationFrame(rafRef.current);
        setTilt({ x: 0, y: 0 });
    }, []);

    /* ── Send message ──────────────────────────────────── */
    const handleSend = useCallback((text: string) => {
        const userMsg: Message = {
            id: Date.now().toString(),
            role: "user",
            content: text,
        };
        setMessages((prev) => [...prev, userMsg]);
        setIsTyping(true);

        setTimeout(() => {
            const reply: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content:
                    MOCK_RESPONSES[responseIndex.current % MOCK_RESPONSES.length],
            };
            responseIndex.current += 1;
            setIsTyping(false);
            setMessages((prev) => [...prev, reply]);
        }, 2000);
    }, []);

    /* ── Memoized panel transform ──────────────────────── */
    const panelStyle = useMemo(
        () => ({
            transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
            transition: "transform 0.35s cubic-bezier(0.23, 1, 0.32, 1)",
            willChange: "transform" as const,
        }),
        [tilt.x, tilt.y]
    );

    return (
        <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-black">
            {/* ── Layer 1: Research grid pattern ────────────── */}
            <div
                className="pointer-events-none absolute inset-0"
                style={{
                    backgroundImage: `url("${GRID_SVG}")`,
                    backgroundSize: "60px 60px",
                    opacity: 1, /* Grid SVG already at 3% opacity */
                }}
            />

            {/* ── Layer 2: Ambient halo diffusion ──────────── */}
            <motion.div
                className="pointer-events-none absolute inset-0"
                style={{
                    background: [
                        "radial-gradient(ellipse 50% 40% at 50% 45%, rgba(34,211,238,0.035) 0%, transparent 60%)",
                        "radial-gradient(ellipse 40% 35% at 52% 48%, rgba(139,92,246,0.02) 0%, transparent 55%)",
                    ].join(", "),
                }}
                animate={{ opacity: [0.6, 1, 0.6] }}
                transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
            />

            {/* ── Layer 3: Depth vignette ──────────────────── */}
            <div
                className="pointer-events-none absolute inset-0"
                style={{
                    background:
                        "radial-gradient(ellipse 75% 75% at 50% 50%, transparent 35%, rgba(0,0,0,0.65) 100%)",
                }}
            />

            {/* ── Chat Panel with perspective tilt ─────────── */}
            <div
                className="relative z-10 w-full px-4"
                style={{
                    perspective: "1400px",
                    display: "flex",
                    justifyContent: "center",
                }}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
            >
                <ChatPanel style={panelStyle}>
                    {/* Header */}
                    <ChatHeader />

                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto py-5">
                        <div className="flex flex-col gap-3">
                            {messages.map((msg, i) => (
                                <ChatMessage key={msg.id} message={msg} index={i} />
                            ))}
                            {isTyping && <TypingIndicator />}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>

                    {/* Input Dock */}
                    <ChatInput onSend={handleSend} />
                </ChatPanel>
            </div>
        </div>
    );
}
