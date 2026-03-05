"use client";

import { memo } from "react";
import { motion } from "framer-motion";

function TypingIndicatorBase() {
  return (
    <motion.div
      className="flex items-center px-6 py-2"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
    >
      <div
        className="flex items-center gap-[5px] rounded-2xl px-4 py-3"
        style={{
          background: "rgba(255,255,255,0.015)",
          backdropFilter: "blur(8px)",
          WebkitBackdropFilter: "blur(8px)",
          border: "1px solid rgba(255,255,255,0.03)",
          boxShadow: "inset 0 1px 0 rgba(255,255,255,0.02)",
        }}
      >
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="block h-[5px] w-[5px] rounded-full"
            style={{ background: "rgba(255,255,255,0.25)" }}
            animate={{ opacity: [0.2, 0.6, 0.2] }}
            transition={{
              duration: 1.8,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.25,
            }}
          />
        ))}
      </div>
    </motion.div>
  );
}

export const TypingIndicator = memo(TypingIndicatorBase);
