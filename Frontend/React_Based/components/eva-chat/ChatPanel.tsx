"use client";

import { memo, type ReactNode, type CSSProperties } from "react";

interface ChatPanelProps {
    style?: CSSProperties;
    children: ReactNode;
}

function ChatPanelBase({ style, children }: ChatPanelProps) {
    return (
        <div className="relative" style={{ ...style }}>
            {/* ── Ambient halo diffusion behind panel ──────── */}
            <div
                className="pointer-events-none absolute -inset-16 -z-10"
                style={{
                    background:
                        "radial-gradient(ellipse 55% 45% at 50% 50%, rgba(34,211,238,0.04) 0%, rgba(139,92,246,0.02) 35%, transparent 70%)",
                    filter: "blur(60px)",
                }}
            />

            {/* ── Panel surface ────────────────────────────── */}
            <div
                className="relative flex flex-col overflow-hidden"
                style={{
                    width: "100%",
                    maxWidth: 900,
                    height: "85vh",
                    borderRadius: "1.5rem",
                    background: "rgba(255,255,255,0.02)",
                    backdropFilter: "blur(48px) saturate(140%)",
                    WebkitBackdropFilter: "blur(48px) saturate(140%)",
                    /* Multi-layer border system: outer subtle, inner top edge highlight */
                    border: "1px solid rgba(255,255,255,0.04)",
                    boxShadow: [
                        /* Outer depth shadow */
                        "0 32px 100px rgba(0,0,0,0.55)",
                        "0 8px 32px rgba(0,0,0,0.3)",
                        /* Inner top-edge luminance highlight */
                        "inset 0 1px 0 rgba(255,255,255,0.04)",
                        /* Ultra-subtle inner side edges */
                        "inset 1px 0 0 rgba(255,255,255,0.02)",
                        "inset -1px 0 0 rgba(255,255,255,0.02)",
                    ].join(", "),
                }}
            >
                {children}
            </div>
        </div>
    );
}

export const ChatPanel = memo(ChatPanelBase);
