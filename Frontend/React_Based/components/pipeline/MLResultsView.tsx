"use client";

import { motion } from "framer-motion";
import { BrainCircuit, ChevronRight, Activity, Cpu } from "lucide-react";

interface MLResultsViewProps {
  mlDetails: Record<string, unknown>;
  onNext: () => void;
}

export function MLResultsView({ mlDetails, onNext }: MLResultsViewProps) {
  const modelName = (mlDetails.selected_model as string) || "Unknown Model";
  const metrics = (mlDetails.metrics as Record<string, number>) || {};

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto mt-12 space-y-8"
    >
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#F97316]/10 border border-[#F97316]/20 mb-4">
          <BrainCircuit className="w-8 h-8 text-[#F97316]" />
        </div>
        <h2 className="text-3xl font-bold text-white">
          Model Evaluation Complete
        </h2>
        <p className="text-white/40 max-w-lg mx-auto">
          The ML Engine has trained and evaluated candidate models, selecting
          the best performing architecture for your data.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div className="bg-[#0A0A0A] border border-white/[0.08] rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#F97316]/5 rounded-full blur-3xl -mr-10 -mt-10" />
          <h3 className="text-sm font-mono text-[#F97316] uppercase tracking-wider flex items-center gap-2 mb-4">
            <Cpu className="w-4 h-4" />
            Selected Architecture
          </h3>
          <div className="text-2xl font-bold text-white mb-2">{modelName}</div>
          <p className="text-sm text-white/40">
            Selected as the champion model based on evaluation metrics across
            validation folds.
          </p>
        </div>

        <div className="bg-[#0A0A0A] border border-white/[0.08] rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full blur-3xl -mr-10 -mt-10" />
          <h3 className="text-sm font-mono text-blue-400 uppercase tracking-wider flex items-center gap-2 mb-4">
            <Activity className="w-4 h-4" />
            Performance Metrics
          </h3>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(metrics).map(([key, value]) => (
              <div key={key} className="space-y-1">
                <div className="text-xs text-white/40 uppercase font-mono">
                  {key.replace(/_/g, " ")}
                </div>
                <div className="text-xl font-semibold text-white">
                  {typeof value === "number"
                    ? value < 1
                      ? (value * 100).toFixed(1) + "%"
                      : value.toFixed(3)
                    : String(value)}
                </div>
              </div>
            ))}
            {Object.keys(metrics).length === 0 && (
              <div className="text-sm text-white/40">No metrics available</div>
            )}
          </div>
        </div>
      </div>

      <div className="flex justify-center mt-12">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onNext}
          className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 hover:bg-white/15 text-white rounded-xl font-semibold transition-colors border border-white/[0.08]"
        >
          Continue to Visualizations
          <ChevronRight className="w-5 h-5" />
        </motion.button>
      </div>
    </motion.div>
  );
}
