import json
from pathlib import Path

from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import (
    GlobalAnalysisLedger,
    ReportMemoryRecord,
)

RULES_PATH = Path(__file__).parent.parent / "rules" / "RGRules.md"
RULES_LITE_PATH = Path(__file__).parent.parent / "rules" / "RGRules.lite.md"


def _load_rules(use_lite: bool = False) -> str:
    path = RULES_LITE_PATH if use_lite else RULES_PATH
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No RG rules file found — generate a reasonable report.)"


class RGAgent:
    """
    Report Generator Agent.
    
    Synthesizes the complete GAL (Sections 1 through 9) into a structured, 
    narrative report document for stakeholders.
    """

    @staticmethod
    def _build_context(gal: GlobalAnalysisLedger) -> str:
        sections = []

        if gal.dataset_identity:
            sections.append("--- SECTION 1: DATASET IDENTITY ---")
            sections.append(gal.dataset_identity.model_dump_json(indent=2))

        if gal.user_intent:
            sections.append("\n--- SECTION 2: USER INTENT ---")
            intent_summary = {
                "primary_objective": gal.user_intent.primary_objective,
                "stakeholder_type": getattr(gal.user_intent, "stakeholder_type", "UNKNOWN"),
            }
            sections.append(json.dumps(intent_summary, indent=2, default=str))

        if gal.data_integrity:
            sections.append("\n--- SECTION 3: DATA INTEGRITY ---")
            sections.append(gal.data_integrity.model_dump_json(indent=2))

        if gal.exploratory_findings:
            sections.append("\n--- SECTION 4: EXPLORATORY FINDINGS ---")
            sections.append(gal.exploratory_findings.model_dump_json(indent=2))

        if gal.hypotheses and isinstance(gal.hypotheses.hypotheses, list):
            sections.append("\n--- SECTION 5: HYPOTHESES ---")
            hyp_data = []
            for h in gal.hypotheses.hypotheses:
                if hasattr(h, "model_dump"):
                    hyp_data.append(h.model_dump())
                elif isinstance(h, dict):
                    hyp_data.append(h)
            sections.append(json.dumps(hyp_data, indent=2, default=str))

        if gal.feature_plan:
            sections.append("\n--- SECTION 6: FEATURE REASONING ---")
            sections.append(gal.feature_plan.model_dump_json(indent=2))

        if gal.visualization_plan and isinstance(gal.visualization_plan.visualizations, list):
            sections.append("\n--- SECTION 7: VISUALIZATION PLAN ---")
            viz_data = []
            for v in gal.visualization_plan.visualizations:
                if hasattr(v, "model_dump"):
                    vd = v.model_dump(exclude={"plotly_config", "chart_file_path"})
                    viz_data.append(vd)
            sections.append(json.dumps(viz_data, indent=2, default=str))

        if gal.dashboard_plan:
            sections.append("\n--- SECTION 9: DASHBOARD PLAN (RECOMMENDATIONS) ---")
            dash_summary = {
                "recommendations": []
            }
            if isinstance(gal.dashboard_plan.recommendations, list):
                for r in gal.dashboard_plan.recommendations:
                    if hasattr(r, "model_dump"):
                        dash_summary["recommendations"].append(r.model_dump())
                    elif isinstance(r, dict):
                        dash_summary["recommendations"].append(r)
            sections.append(json.dumps(dash_summary, indent=2, default=str))

        return "\n".join(sections)

    @staticmethod
    def execute(gal: GlobalAnalysisLedger, rules_mode: str = "full") -> ReportMemoryRecord:
        """Execute the RG agent to generate a narrative report."""
        use_lite = rules_mode == "lite"
        rules = _load_rules(use_lite=use_lite)

        system_prompt = f"""You are EVA's Report Generator.
You MUST respond in English only.

{rules}"""

        context = RGAgent._build_context(gal)

        user_prompt = f"""Analyze the following complete GAL context and generate the final narrative report.

{context}

Generate the report following your architectural rules. Remember:
- Do NOT perform new statistical analysis.
- Be honest about uncertainty and missing evidence.
- Ensure the complexity and tone match the stakeholder_type.
- Provide a flowing markdown narrative in the `narrative` field.
- Output ONLY valid JSON matching the ReportMemoryRecord schema.

Now write the detailed narrative report based exclusively on the data above."""

        # Use an advanced reasoning model for long-form narrative generation
        result = invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=ReportMemoryRecord,
            model_type="reasoning", 
        )

        return result
