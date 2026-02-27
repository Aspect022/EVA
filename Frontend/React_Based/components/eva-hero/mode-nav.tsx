"use client";

import { ChevronUp, ChevronDown } from "lucide-react";
import type { ModeVariant } from "./hero-config";

interface ModeNavProps {
    modes: ModeVariant[];
    activeIndex: number;
    onPrev: () => void;
    onNext: () => void;
    scrollProgress: number;
}

export function ModeNav({ modes, activeIndex, onPrev, onNext, scrollProgress }: ModeNavProps) {
    // Reverse parallax: nav moves DOWN as user scrolls DOWN (opposite to text)
    const navY = scrollProgress * 40;
    const opacity = Math.max(0, 1 - scrollProgress * 1.5);

    return (
        <div
            className="absolute right-6 lg:right-12 top-1/2 -translate-y-1/2 z-30 flex flex-col items-center gap-6"
            style={{
                transform: `translateY(calc(-50% + ${navY}px))`,
                opacity,
            }}
        >
            {/* Large Index Number */}
            <p
                className="text-6xl lg:text-8xl font-black text-white/[0.07] leading-none select-none"
                style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
            >
                {String(activeIndex + 1).padStart(2, "0")}
            </p>

            {/* PREV */}
            <button
                onClick={onPrev}
                className="flex flex-col items-center gap-1 group transition-colors"
                aria-label="Previous mode"
            >
                <ChevronUp className="w-4 h-4 text-white/30 group-hover:text-white/80 transition-colors" />
                <span
                    className="text-[10px] tracking-[0.2em] text-white/30 group-hover:text-white/80 transition-colors uppercase"
                    style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                >
                    Prev
                </span>
            </button>

            {/* Vertical Divider with mode dots */}
            <div className="flex flex-col items-center gap-3 py-2">
                {modes.map((mode, i) => (
                    <div
                        key={mode.id}
                        className="w-[3px] h-6 rounded-full transition-all duration-500"
                        style={{
                            backgroundColor:
                                i === activeIndex
                                    ? mode.accent
                                    : "rgba(255,255,255,0.1)",
                            boxShadow:
                                i === activeIndex
                                    ? `0 0 8px ${mode.accent}60`
                                    : "none",
                        }}
                    />
                ))}
            </div>

            {/* NEXT */}
            <button
                onClick={onNext}
                className="flex flex-col items-center gap-1 group transition-colors"
                aria-label="Next mode"
            >
                <span
                    className="text-[10px] tracking-[0.2em] text-white/30 group-hover:text-white/80 transition-colors uppercase"
                    style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                >
                    Next
                </span>
                <ChevronDown className="w-4 h-4 text-white/30 group-hover:text-white/80 transition-colors" />
            </button>
        </div>
    );
}
