"use client";

import { useState, useRef, useCallback } from "react";
import { MODES, HERO_SCROLL_HEIGHT_VH } from "./hero-config";
import { useScrollProgress } from "@/hooks/use-scroll-progress";
import { LoadingOverlay } from "./loading-overlay";
import { BrainCanvas } from "./brain-canvas";
import { HeroTextOverlay } from "./hero-text-overlay";
import { ModeNav } from "./mode-nav";

export function EvaHero() {
    const [isLoading, setIsLoading] = useState(true);
    const [activeModeIndex, setActiveModeIndex] = useState(0);
    const containerRef = useRef<HTMLDivElement>(null);
    const scrollProgress = useScrollProgress(containerRef);

    const activeMode = MODES[activeModeIndex];

    const handleLoadComplete = useCallback(() => {
        setIsLoading(false);
    }, []);

    const handlePrev = useCallback(() => {
        setActiveModeIndex((i) => (i - 1 + MODES.length) % MODES.length);
    }, []);

    const handleNext = useCallback(() => {
        setActiveModeIndex((i) => (i + 1) % MODES.length);
    }, []);

    return (
        <>
            {/* Loading overlay */}
            {isLoading && <LoadingOverlay onComplete={handleLoadComplete} />}

            {/* Scrollable container — height drives scroll progress */}
            <div
                ref={containerRef}
                style={{ height: `${HERO_SCROLL_HEIGHT_VH}vh` }}
                className="relative"
            >
                {/* Sticky viewport */}
                <div className="sticky top-0 h-screen w-full overflow-hidden bg-black">
                    {/* Brain Canvas — RIGHT side */}
                    <BrainCanvas
                        scrollProgress={scrollProgress}
                        activeMode={activeMode}
                        className="absolute top-0 right-0 w-[60%] h-full"
                    />

                    {/* Subtle gradient overlay for depth between text and brain */}
                    <div
                        className="absolute inset-0 pointer-events-none z-10"
                        style={{
                            background:
                                "linear-gradient(90deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 35%, rgba(0,0,0,0) 55%)",
                        }}
                    />

                    {/* Text Overlay — LEFT side */}
                    <HeroTextOverlay
                        mode={activeMode}
                        modeIndex={activeModeIndex}
                        scrollProgress={scrollProgress}
                    />

                    {/* Mode Navigation — RIGHT edge */}
                    <ModeNav
                        modes={MODES}
                        activeIndex={activeModeIndex}
                        onPrev={handlePrev}
                        onNext={handleNext}
                        scrollProgress={scrollProgress}
                    />

                    {/* Scroll indicator at bottom */}
                    <div
                        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-2 transition-opacity duration-500"
                        style={{ opacity: scrollProgress < 0.1 ? 1 : 0 }}
                    >
                        <span
                            className="text-[10px] tracking-[0.3em] text-white/30 uppercase"
                            style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                        >
                            Scroll to explore
                        </span>
                        <div className="w-[1px] h-6 bg-white/20 animate-pulse" />
                    </div>

                    {/* Bottom gradient fade */}
                    <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black to-transparent pointer-events-none z-10" />
                </div>
            </div>
        </>
    );
}
