"use client";

import { useState, useRef, useCallback, useEffect } from "react";
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
    const previousModeIndexRef = useRef(0);
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

    // When we reach mode 3 (index 2), smoothly scroll to the next section after the hero
    useEffect(() => {
        if (activeModeIndex === 2 && previousModeIndexRef.current !== 2) {
            const nextSection = document.getElementById("next-section");
            if (nextSection) {
                nextSection.scrollIntoView({ behavior: "smooth" });
            } else {
                const scrollAmount = window.innerHeight * 0.15;
                window.scrollBy({
                    top: scrollAmount,
                    behavior: "smooth",
                });
            }
        }

        previousModeIndexRef.current = activeModeIndex;
    }, [activeModeIndex]);

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

                    {/* Hero-only Parallax video in bottom-right corner */}
                    <div
                        className="absolute bottom-6 right-6 z-30 pointer-events-none"
                        style={{
                            opacity: Math.max(0, 1 - scrollProgress * 2),
                            transition: "opacity 300ms ease-out",
                        }}
                    >
                        <video
                            src="/Parallax.mp4"
                            autoPlay
                            muted
                            loop
                            playsInline
                            className="w-40 h-40 md:w-56 md:h-56 lg:w-64 lg:h-64 rounded-full border border-white/15 shadow-[0_0_40px_rgba(0,0,0,0.9)] object-cover overflow-hidden"
                        />
                    </div>

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
