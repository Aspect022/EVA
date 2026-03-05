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
  const isScrollLockedRef = useRef(false);
  const scrollProgress = useScrollProgress(containerRef);

  const activeMode = MODES[activeModeIndex];

  const handleLoadComplete = useCallback(() => {
    setIsLoading(false);
  }, []);

  const handlePrev = useCallback(() => {
    const heroEl = containerRef.current;
    if (heroEl) {
      const segmentHeight = heroEl.clientHeight / MODES.length;
      window.scrollBy({ top: -segmentHeight, behavior: "smooth" });
    }
  }, []);

  const handleNext = useCallback(() => {
    const heroEl = containerRef.current;
    if (heroEl) {
      const segmentHeight = heroEl.clientHeight / MODES.length;
      window.scrollBy({ top: segmentHeight, behavior: "smooth" });
    }
  }, []);

  // Handle Scroll Locking
  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
      if (isScrollLockedRef.current) e.preventDefault();
    };
    const handleTouchMove = (e: TouchEvent) => {
      if (isScrollLockedRef.current) e.preventDefault();
    };

    // Must be non-passive to allow preventDefault
    window.addEventListener("wheel", handleWheel, { passive: false });
    window.addEventListener("touchmove", handleTouchMove, { passive: false });

    return () => {
      window.removeEventListener("wheel", handleWheel);
      window.removeEventListener("touchmove", handleTouchMove);
    };
  }, []);

  // Update active mode based on scroll progress and trigger lock
  useEffect(() => {
    // Calculate which mode should be active based on scroll progress (0 to 1)
    const newIndex = Math.max(
      0,
      Math.min(
        Math.floor((scrollProgress + 0.05) * MODES.length), // slight offset to trigger a bit earlier
        MODES.length - 1,
      ),
    );

    if (newIndex !== activeModeIndex && !Number.isNaN(newIndex)) {
      setActiveModeIndex(newIndex);

      // Lock scrolling for 1 second on transition
      isScrollLockedRef.current = true;
      setTimeout(() => {
        isScrollLockedRef.current = false;
      }, 1000);
    }
  }, [scrollProgress, activeModeIndex]);

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

          {/* Hero-only Parallax video in bottom-right corner - Holographic Projector Base */}
          <div
            className="absolute bottom-10 right-4 md:right-10 z-30 pointer-events-none flex flex-col items-center justify-end"
            style={{
              width: "300px",
              height: "350px",
            }}
          >
            {/* Video - floating holographic element */}
            <video
              src="/Parallax.mp4"
              autoPlay
              muted
              loop
              playsInline
              className="w-48 h-48 md:w-64 md:h-64 lg:w-72 lg:h-72 object-cover"
              style={{
                mixBlendMode: "screen",
                transform: "translateY(30px)",
                zIndex: 10,
                WebkitMaskImage:
                  "radial-gradient(circle, rgba(0,0,0,1) 50%, rgba(0,0,0,0) 70%)",
                maskImage:
                  "radial-gradient(circle, rgba(0,0,0,1) 40%, rgba(0,0,0,0) 65%)",
              }}
            />

            {/* Hologram Projector Base */}
            <div className="relative w-48 h-12 mt-[-20px] z-1 opacity-90">
              {/* Central Light Beam */}
              <div
                className="absolute bottom-6 left-1/2 -translate-x-1/2 w-[140%] h-48 origin-bottom"
                style={{
                  background:
                    "linear-gradient(to top, rgba(0, 180, 255, 0.4) 0%, rgba(0, 200, 255, 0.1) 60%, transparent 100%)",
                  clipPath: "polygon(15% 0, 85% 0, 58% 100%, 42% 100%)",
                  filter: "blur(6px)",
                }}
              />
              {/* Top glowing elliptical plate */}
              <div className="absolute top-0 left-0 w-full h-8 bg-blue-900/40 rounded-[50%] border-[2px] border-cyan-400 shadow-[0_0_25px_rgba(0,180,255,0.7),inset_0_0_15px_rgba(0,180,255,0.8)] z-10" />

              {/* Mid base cylinder body */}
              <div className="absolute top-4 left-0 w-full h-8 bg-gradient-to-b from-[#0a192f] to-[#020c1b] rounded-[50%] border-x border-b border-cyan-600/50 shadow-[0_15px_25px_rgba(0,0,0,0.9)] overflow-hidden z-0">
                {/* Segment lines mimicking machinery/alien tech */}
                <div className="absolute inset-0 bg-[repeating-linear-gradient(90deg,transparent,transparent_20px,rgba(0,255,255,0.15)_20px,rgba(0,255,255,0.15)_21px)]" />
                {/* Bottom glowing accent line */}
                <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-60 flex justify-center items-center" />
              </div>

              {/* Center glowing core emitter */}
              <div className="absolute top-2 left-1/2 -translate-x-1/2 w-16 h-4 bg-cyan-200 rounded-[50%] shadow-[0_0_15px_#00ffff,0_0_30px_#00ffff] z-20" />
              <div className="absolute top-3 left-1/2 -translate-x-1/2 w-8 h-2 bg-white rounded-[50%] shadow-[0_0_10px_#ffffff] z-30" />
            </div>
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
              style={{
                fontFamily: "var(--font-fira-code, 'Fira Code', monospace)",
              }}
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
