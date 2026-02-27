export interface ModeVariant {
    id: string;
    name: string;
    subtitle: string;
    description: string;
    accent: string;
    frameCount: number;
    /** Canvas visual config */
    visual: {
        nodeCount: number;
        connectionDensity: number;
        pulseSpeed: number;
        innerGlow: string;
    };
}

export const MODES: ModeVariant[] = [
    {
        id: "baseline",
        name: "BASELINE",
        subtitle: "RAPID ANALYTICAL MODE",
        description:
            "Fast, conversational, and low compute. Perfect for quick dataset profiling, column explanations, and gaining a baseline understanding without heavy pipelines.",
        accent: "#3B82F6",
        frameCount: 240,
        visual: {
            nodeCount: 60,
            connectionDensity: 0.35,
            pulseSpeed: 1.0,
            innerGlow: "rgba(59, 130, 246, 0.15)",
        },
    },
    {
        id: "full-pipeline",
        name: "FULL PIPELINE",
        subtitle: "DEEP INVESTIGATION MODE",
        description:
            "Activated automatically for prediction, risk scoring, and forecasting. The true power of EVA\u2019s multi-agent Machine Learning reasoning pipeline.",
        accent: "#F97316",
        frameCount: 240,
        visual: {
            nodeCount: 120,
            connectionDensity: 0.55,
            pulseSpeed: 1.6,
            innerGlow: "rgba(249, 115, 22, 0.15)",
        },
    },
    {
        id: "hitl-gate",
        name: "HITL GATE",
        subtitle: "HUMAN-IN-THE-LOOP",
        description:
            "A prominent decision gate that asks the user to accept or reject a hypothesis to unlock ML execution, keeping you in full structural control.",
        accent: "#22D3EE",
        frameCount: 240,
        visual: {
            nodeCount: 80,
            connectionDensity: 0.4,
            pulseSpeed: 0.8,
            innerGlow: "rgba(34, 211, 238, 0.15)",
        },
    },
];

export const HERO_SCROLL_HEIGHT_VH = 300;
export const TRANSITION_DURATION_MS = 600;
