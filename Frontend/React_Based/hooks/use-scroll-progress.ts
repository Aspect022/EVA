"use client";

import { useState, useEffect, useCallback, useRef } from "react";

/**
 * Returns a scroll progress value between 0 and 1
 * based on how far the user has scrolled within a ref element.
 */
export function useScrollProgress(containerRef: React.RefObject<HTMLElement | null>) {
    const [progress, setProgress] = useState(0);
    const rafId = useRef<number>(0);

    const handleScroll = useCallback(() => {
        if (rafId.current) cancelAnimationFrame(rafId.current);
        rafId.current = requestAnimationFrame(() => {
            if (!containerRef.current) return;
            const rect = containerRef.current.getBoundingClientRect();
            const scrollableHeight = containerRef.current.scrollHeight - window.innerHeight;
            if (scrollableHeight <= 0) {
                setProgress(0);
                return;
            }
            // How far from top of container to top of viewport
            const scrolled = -rect.top;
            const p = Math.max(0, Math.min(1, scrolled / scrollableHeight));
            setProgress(p);
        });
    }, [containerRef]);

    useEffect(() => {
        window.addEventListener("scroll", handleScroll, { passive: true });
        handleScroll();
        return () => {
            window.removeEventListener("scroll", handleScroll);
            if (rafId.current) cancelAnimationFrame(rafId.current);
        };
    }, [handleScroll]);

    return progress;
}
