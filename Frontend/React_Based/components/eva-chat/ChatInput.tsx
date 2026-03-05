"use client";

import { memo, useState, useCallback, type KeyboardEvent } from "react";
import { motion } from "framer-motion";
import { Send } from "lucide-react";

interface ChatInputProps {
    onSend: (text: string) => void;
}

function ChatInputBase({ onSend }: ChatInputProps) {
    const [value, setValue] = useState("");
    const [focused, setFocused] = useState(false);

    const handleSend = useCallback(() => {
        const trimmed = value.trim();
        if (!trimmed) return;
        onSend(trimmed);
        setValue("");
    }, [value, onSend]);

    const handleKeyDown = useCallback(
        (e: KeyboardEvent<HTMLInputElement>) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        },
        [handleSend]
    );

    const hasValue = value.trim().length > 0;

    return (
        <motion.div
            className="px-6 pb-6 pt-3"
            style={{
                borderTop: "1px solid rgba(255,255,255,0.03)",
                boxShadow: "inset 0 1px 0 rgba(255,255,255,0.015)",
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.3, ease: "easeOut" }}
        >
            <div
                className="flex items-center gap-3 rounded-full px-5 py-3"
                style={{
                    background: "rgba(255,255,255,0.02)",
                    backdropFilter: "blur(16px)",
                    WebkitBackdropFilter: "blur(16px)",
                    border: `1px solid ${focused
                            ? "rgba(34,211,238,0.1)"
                            : "rgba(255,255,255,0.04)"
                        }`,
                    boxShadow: focused
                        ? "0 0 24px rgba(34,211,238,0.06), 0 0 8px rgba(34,211,238,0.04), inset 0 1px 0 rgba(255,255,255,0.03)"
                        : "inset 0 1px 0 rgba(255,255,255,0.02)",
                    transition: "border-color 0.3s ease, box-shadow 0.4s ease",
                }}
            >
                <input
                    type="text"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    onFocus={() => setFocused(true)}
                    onBlur={() => setFocused(false)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask EVA anything..."
                    className="flex-1 bg-transparent text-[13.5px] outline-none"
                    style={{
                        color: "rgba(255,255,255,0.8)",
                        letterSpacing: "-0.005em",
                    }}
                />
                {/* Placeholder color via global css or inline not possible cleanly —
            we use a wrapper style tag in the component */}
                <style>{`
          .flex-1::placeholder {
            color: rgba(255,255,255,0.16);
          }
        `}</style>
                <button
                    onClick={handleSend}
                    disabled={!hasValue}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
                    style={{
                        background: hasValue
                            ? "rgba(34,211,238,0.08)"
                            : "rgba(255,255,255,0.025)",
                        border: `1px solid ${hasValue
                                ? "rgba(34,211,238,0.12)"
                                : "rgba(255,255,255,0.04)"
                            }`,
                        boxShadow: hasValue
                            ? "0 0 12px rgba(34,211,238,0.06)"
                            : "none",
                        transition: "all 0.3s ease",
                        cursor: hasValue ? "pointer" : "default",
                    }}
                    onMouseEnter={(e) => {
                        if (hasValue) {
                            const el = e.currentTarget as HTMLButtonElement;
                            el.style.boxShadow = "0 0 18px rgba(34,211,238,0.12)";
                            el.style.borderColor = "rgba(34,211,238,0.2)";
                        }
                    }}
                    onMouseLeave={(e) => {
                        const el = e.currentTarget as HTMLButtonElement;
                        el.style.boxShadow = hasValue
                            ? "0 0 12px rgba(34,211,238,0.06)"
                            : "none";
                        el.style.borderColor = hasValue
                            ? "rgba(34,211,238,0.12)"
                            : "rgba(255,255,255,0.04)";
                    }}
                    aria-label="Send message"
                >
                    <Send
                        size={13}
                        style={{
                            color: hasValue
                                ? "rgba(34,211,238,0.65)"
                                : "rgba(255,255,255,0.2)",
                            transition: "color 0.3s ease",
                        }}
                    />
                </button>
            </div>
        </motion.div>
    );
}

export const ChatInput = memo(ChatInputBase);
