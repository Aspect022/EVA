"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface LoadingOverlayProps {
    onComplete: () => void;
}

export function LoadingOverlay({ onComplete }: LoadingOverlayProps) {
    const [progress, setProgress] = useState(0);
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        const duration = 2200; // ms total
        const interval = 30;
        let elapsed = 0;

        const timer = setInterval(() => {
            elapsed += interval;
            // Ease-out progression
            const t = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3);
            setProgress(Math.round(eased * 100));

            if (elapsed >= duration) {
                clearInterval(timer);
                setTimeout(() => {
                    setVisible(false);
                    setTimeout(onComplete, 500);
                }, 300);
            }
        }, interval);

        return () => clearInterval(timer);
    }, [onComplete]);

    return (
        <AnimatePresence>
            {visible && (
                <motion.div
                    initial={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                    className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black"
                >
                    {/* EVA Logo */}
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1, duration: 0.5 }}
                        className="mb-12"
                    >
                        <h1
                            className="text-5xl font-bold tracking-[0.3em]"
                            style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                        >
                            <span className="text-white">E</span>
                            <span className="text-[#3B82F6]">V</span>
                            <span className="text-white">A</span>
                        </h1>
                    </motion.div>

                    {/* Progress bar */}
                    <div className="w-64 sm:w-80">
                        <div className="h-[2px] w-full bg-white/10 rounded-full overflow-hidden">
                            <motion.div
                                className="h-full rounded-full"
                                style={{
                                    width: `${progress}%`,
                                    background: "linear-gradient(90deg, #3B82F6, #F97316)",
                                }}
                                transition={{ duration: 0.05 }}
                            />
                        </div>

                        {/* Status text */}
                        <p
                            className="mt-4 text-xs text-white/40 text-center tracking-wider"
                            style={{ fontFamily: "var(--font-fira-code, 'Fira Code', monospace)" }}
                        >
                            Initializing Global Analysis Ledger{" "}
                            <span className="text-[#3B82F6]">{progress}%</span>
                        </p>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
