"use client";

import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import type { ModeVariant } from "./hero-config";

interface HeroTextOverlayProps {
    mode: ModeVariant;
    modeIndex: number;
    scrollProgress: number;
}

export function HeroTextOverlay({ mode, modeIndex, scrollProgress }: HeroTextOverlayProps) {
    // Reverse parallax: text moves UP as user scrolls DOWN
    const textY = scrollProgress * -80;
    const opacity = Math.max(0, 1 - scrollProgress * 1.8);

    return (
        <div
            className="absolute top-0 left-0 w-[45%] h-full flex flex-col justify-center z-20 pl-10 lg:pl-20 xl:pl-28"
            style={{
                transform: `translateY(${textY}px)`,
                opacity,
            }}
        >
            {/* EVA Logo */}
            <div className="mb-8">
                <Image
                    src="/logo.png"
                    alt="EVA"
                    width={100}
                    height={44}
                    className="h-[36px] w-auto object-contain brightness-0 invert"
                    priority
                />
            </div>

            {/* Mode Content with Animated Transitions */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={mode.id}
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 30 }}
                    transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
                >
                    {/* Mode Index (small) */}
                    <p
                        className="text-xs tracking-[0.2em] mb-3"
                        style={{
                            color: mode.accent,
                            fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
                        }}
                    >
                        MODE {String(modeIndex + 1).padStart(2, "0")}
                    </p>

                    {/* Mode Name */}
                    <h1
                        className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-black tracking-tight leading-none mb-3"
                        style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                    >
                        {mode.name}
                    </h1>

                    {/* Subtitle */}
                    <p
                        className="text-sm md:text-base tracking-[0.15em] mb-6"
                        style={{
                            color: mode.accent,
                            fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
                        }}
                    >
                        {mode.subtitle}
                    </p>

                    {/* Description */}
                    <p className="text-sm md:text-base text-white/50 leading-relaxed max-w-md mb-10">
                        {mode.description}
                    </p>

                    {/* CTA Buttons */}
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => document.getElementById("gal-trace")?.scrollIntoView({ behavior: "smooth" })}
                            className="px-6 py-3 rounded-full border text-sm font-medium tracking-wide transition-all duration-300 hover:bg-white/5"
                            style={{
                                borderColor: "#3B82F6",
                                color: "#FFFFFF",
                            }}
                        >
                            VIEW GAL TRACE
                        </button>
                        <Link
                            href="/dashboard"
                            className="px-6 py-3 rounded-full text-sm font-medium tracking-wide text-white transition-all duration-300 hover:brightness-110"
                            style={{
                                backgroundColor: "#F97316",
                            }}
                        >
                            START SESSION
                        </Link>
                    </div>
                </motion.div>
            </AnimatePresence>
        </div>
    );
}
