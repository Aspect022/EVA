import json
from pathlib import Path
from typing import Dict, Any

from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import (
    DashboardPlanRecord,
    DatasetIdentity,
    UserIntentRecord,
    ExploratoryFindings,
    HypothesesRecord,
    VisualizationPlanRecord,
)

RULES_PATH = Path(__file__).parent.parent / "rules" / "ADCRules.md"
RULES_LITE_PATH = Path(__file__).parent.parent / "rules" / "ADCRules.lite.md"


def _load_rules(use_lite: bool = False) -> str:
    path = RULES_LITE_PATH if use_lite else RULES_PATH
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No ADC rules file found — generate a reasonable dashboard plan.)"


class ADCAgent:
    """
    Analytical Dashboard Composer Agent.
    
    Synthesizes insights from the GAL (Findings, Hypotheses, Visualizations)
    into a structured Dashboard Plan (KPIs, Alerts, Recommendations).
    """

    @staticmethod
    def _build_context(
        identity: DatasetIdentity,
        intent: UserIntentRecord | None,
        findings: ExploratoryFindings | None,
        hypotheses: HypothesesRecord | None,
        viz_plan: VisualizationPlanRecord | None,
    ) -> str:
        sections = []

        if identity:
            sections.append("--- SECTION 1: DATASET IDENTITY ---")
            sections.append(identity.model_dump_json(indent=2))

        if intent:
            sections.append("\n--- SECTION 2: USER INTENT ---")
            intent_summary = {
                "primary_objective": intent.primary_objective,
                "stakeholder_type": getattr(intent, "stakeholder_type", "UNKNOWN"),
                "decision_impact": getattr(intent, "decision_impact", "UNKNOWN"),
            }
            sections.append(json.dumps(intent_summary, indent=2, default=str))

        if findings:
            sections.append("\n--- SECTION 4: EXPLORATORY FINDINGS ---")
            findings_data = {
                "anomalies": findings.anomalies,
                "target_associations": findings.target_associations,
                "overall_reasoning": findings.overall_reasoning,
            }
            sections.append(json.dumps(findings_data, indent=2, default=str))

        if hypotheses and isinstance(hypotheses.hypotheses, list):
            sections.append("\n--- SECTION 5: HYPOTHESES ---")
            hyp_data = []
            for h in hypotheses.hypotheses:
                if hasattr(h, "model_dump"):
                    hyp_data.append(h.model_dump())
                elif isinstance(h, dict):
                    hyp_data.append(h)
            sections.append(json.dumps(hyp_data, indent=2, default=str))

        if viz_plan and isinstance(viz_plan.visualizations, list):
            sections.append("\n--- SECTION 7: VISUALIZATION PLAN ---")
            viz_data = []
            for v in viz_plan.visualizations:
                if hasattr(v, "model_dump"):
                    vd = v.model_dump(exclude={"plotly_config", "chart_file_path"})
                    viz_data.append(vd)
            sections.append(json.dumps(viz_data, indent=2, default=str))

        return "\n".join(sections)

    @staticmethod
    def execute(
        identity: DatasetIdentity,
        intent: UserIntentRecord | None = None,
        findings: ExploratoryFindings | None = None,
        hypotheses: HypothesesRecord | None = None,
        viz_plan: VisualizationPlanRecord | None = None,
        rules_mode: str = "full",
    ) -> DashboardPlanRecord:
        """Execute the ADC agent to generate a dashboard plan."""
        use_lite = rules_mode == "lite"
        rules = _load_rules(use_lite=use_lite)

        system_prompt = f"""You are EVA's Analytical Dashboard Composer.
You MUST respond in English only.

{rules}"""

        context = ADCAgent._build_context(identity, intent, findings, hypotheses, viz_plan)

        user_prompt = f"""Analyze the following GAL context and create a dashboard plan.

{context}

Generate a dashboard plan following your rules. Remember:
- Do NOT hallucinate metric values for KPIs.
- Ensure recommendations are strictly bound by hypothesis plausibility.
- Output ONLY valid JSON matching the DashboardPlanRecord schema.

Now construct the Dashboard Plan based on the actual data above. Fill in EVERY field with specific, detailed content relevant to this dataset."""

        # Use an advanced reasoning model for complex structuring
        result = invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=DashboardPlanRecord,
            model_type="reasoning", 
        )

        return result
