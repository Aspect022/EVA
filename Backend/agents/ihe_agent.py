import json
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional

from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import (
    HypothesisEntry,
    HypothesesRecord,
    DatasetIdentity,
    UserIntentRecord,
    DataIntegrityRecord,
    ExploratoryFindings,
    _coerce_to_list,
)

RULES_PATH = Path(__file__).parent.parent / "rules" / "IHERules.md"
RULES_LITE_PATH = Path(__file__).parent.parent / "rules" / "IHERules.lite.md"


def _load_rules(use_lite: bool = False) -> str:
    path = RULES_LITE_PATH if use_lite else RULES_PATH
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No IHE rules file found — use conservative hypothesis generation.)"


# --- LLM-facing schema (clean, no recorded_at) ---
class HypothesisOutput(BaseModel):
    """What the LLM returns — list of hypotheses with metadata."""
    hypotheses: Optional[List[HypothesisEntry] | str] = Field(default_factory=list)
    significant_findings_count: int = Field(default=0)
    skipped_findings_count: int = Field(default=0)
    overall_reasoning: str = Field(default="")

    @field_validator("hypotheses", mode="before")
    @classmethod
    def coerce_hypotheses(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [{"hypothesis": v}]
        return v


class IHEAgent:
    """
    Investigation & Hypothesis Engine Agent.

    Reads GAL Sections 1–4 and generates structured, evidence-backed hypotheses
    about WHY observed patterns exist in the real world.
    """

    @staticmethod
    def _build_context(
        identity: DatasetIdentity,
        intent: UserIntentRecord | None,
        integrity: DataIntegrityRecord | None,
        findings: ExploratoryFindings,
    ) -> str:
        """Assemble the full GAL context into a prompt-ready string."""
        sections = []

        # Section 1
        sections.append("--- SECTION 1: DATASET IDENTITY ---")
        sections.append(identity.model_dump_json(indent=2))

        # Section 2
        if intent:
            sections.append("\n--- SECTION 2: USER INTENT ---")
            intent_summary = {
                "primary_objective": intent.primary_objective,
                "selected_target": intent.selected_target,
                "analytical_goal": intent.analytical_goal,
                "decision_supported": intent.decision_supported,
                "deployment_mode": intent.deployment_mode,
                "risk_tier": intent.risk_tier,
            }
            sections.append(json.dumps(intent_summary, indent=2, default=str))

        # Section 3
        if integrity:
            sections.append("\n--- SECTION 3: DATA INTEGRITY RECORD ---")
            integrity_summary = {
                "validation_result": integrity.validation_result,
                "overall_reasoning": integrity.overall_reasoning,
                "modifications_count": len(integrity.modifications) if isinstance(integrity.modifications, list) else 0,
            }
            sections.append(json.dumps(integrity_summary, indent=2, default=str))

        # Section 4
        sections.append("\n--- SECTION 4: EXPLORATORY FINDINGS ---")
        findings_data = {
            "distributions": findings.distributions,
            "correlations": findings.correlations,
            "anomalies": findings.anomalies,
            "target_associations": findings.target_associations,
            "overall_reasoning": findings.overall_reasoning,
        }
        sections.append(json.dumps(findings_data, indent=2, default=str))

        return "\n".join(sections)

    @staticmethod
    def execute(
        identity: DatasetIdentity,
        findings: ExploratoryFindings,
        intent: UserIntentRecord | None = None,
        integrity: DataIntegrityRecord | None = None,
        rules_mode: str = "full",
    ) -> HypothesesRecord:
        """
        Run the IHE agent: read GAL Sections 1–4, invoke reasoning LLM,
        return a validated HypothesesRecord for Section 5.
        """
        try:
            use_lite = rules_mode == "lite"
            rules = _load_rules(use_lite=use_lite)

            system_prompt = f"""You are EVA's Investigation & Hypothesis Engine.
You MUST respond in English only.

{rules}"""

            context = IHEAgent._build_context(identity, intent, integrity, findings)

            # Concrete example so the LLM fills in REAL content, not empty placeholders
            concrete_example = '''{
  "hypotheses": [
    {
      "observation_ref": "correlation_fare_survival",
      "observation_plain_language": "Passengers who paid higher fares were significantly more likely to survive",
      "hypothesis": "Higher-fare passengers occupied upper decks closer to lifeboats, giving them faster access during evacuation",
      "supporting_evidence": ["Strong positive correlation between Fare and Survived", "Pclass=1 passengers had highest fare AND highest survival rate"],
      "contradicting_evidence": ["No direct deck/cabin data available to confirm proximity to lifeboats"],
      "missing_evidence": ["Lifeboat assignment records", "Cabin deck mapping to confirm physical proximity"],
      "plausibility": "High",
      "reasoning": "The fare-survival link is consistent with well-documented preferential access to lifeboats for upper-class passengers. Multiple data points converge on this explanation.",
      "confidence_note": "While the statistical relationship is strong, the causal mechanism (deck proximity) cannot be directly confirmed from this dataset alone."
    },
    {
      "observation_ref": "correlation_fare_survival",
      "observation_plain_language": "Passengers who paid higher fares were significantly more likely to survive",
      "hypothesis": "Wealthier passengers received preferential treatment from crew during the evacuation process",
      "supporting_evidence": ["Class-based survival disparity is consistent across all fare levels"],
      "contradicting_evidence": ["No direct evidence of crew bias in the dataset"],
      "missing_evidence": ["Crew testimony records", "Evacuation order documentation"],
      "plausibility": "Moderate",
      "reasoning": "Plausible given historical accounts but not directly supported by the dataset. The data shows the outcome (survival disparity) but not the mechanism (crew behavior).",
      "confidence_note": "This hypothesis relies on external historical knowledge rather than dataset evidence."
    }
  ],
  "significant_findings_count": 3,
  "skipped_findings_count": 2,
  "overall_reasoning": "Focused on the strongest patterns: socioeconomic survival disparity, age effects, and family presence. Each received multiple competing hypotheses with evidence assessment."
}'''

            user_prompt = f"""Analyze the following GAL context and generate hypotheses for significant findings.

{context}

Generate hypotheses following the 5-step process in your rules. Remember:
- At least 2 hypotheses per significant observation
- Always record contradicting evidence
- Use domain-appropriate language
- Assign plausibility based on evidence, not appeal
- EVERY field must be filled with real content — do NOT leave any field empty

Here is an EXAMPLE of the expected output format with FILLED-IN content:
{concrete_example}

Now generate YOUR hypotheses based on the actual data above. Fill in EVERY field with specific, detailed content relevant to this dataset."""

            result = invoke_agent(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                pydantic_schema=HypothesisOutput,
                model_type="reasoning",
            )

            # Filter out any empty hypothesis entries the LLM may have returned
            valid_hypotheses = []
            if isinstance(result.hypotheses, list):
                for h in result.hypotheses:
                    if isinstance(h, HypothesisEntry) and h.hypothesis.strip():
                        valid_hypotheses.append(h)

            return HypothesesRecord(
                hypotheses=valid_hypotheses,
                significant_findings_count=result.significant_findings_count,
                skipped_findings_count=result.skipped_findings_count,
                overall_reasoning=result.overall_reasoning,
            )

        except Exception as e:
            raise Exception(f"IHE Agent execution failed: {str(e)}")
