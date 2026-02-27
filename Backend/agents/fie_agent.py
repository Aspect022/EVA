import json
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional

from Backend.agents.llm_core import invoke_agent
from Backend.rag.rag_loader import load_rag_context
from Backend.models.gal_schema import (
    FeatureEntry,
    FeaturePlanRecord,
    DatasetIdentity,
    UserIntentRecord,
    DataIntegrityRecord,
    ExploratoryFindings,
    HypothesesRecord,
    _coerce_to_list,
)

RULES_PATH = Path(__file__).parent.parent / "rules" / "FIERules.md"
RULES_LITE_PATH = Path(__file__).parent.parent / "rules" / "FIERules.lite.md"


def _load_rules(use_lite: bool = False) -> str:
    path = RULES_LITE_PATH if use_lite else RULES_PATH
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No FIE rules file found — use general feature engineering principles.)"


# --- LLM-facing schema ---
class FeatureOutput(BaseModel):
    """What the LLM returns — feature plan with metadata."""
    domain: str = Field(default="UNKNOWN")
    problem_type: str = Field(default="UNKNOWN")
    features: Optional[List[FeatureEntry] | str] = Field(default_factory=list)
    overall_reasoning: str = Field(default="")

    @field_validator("features", mode="before")
    @classmethod
    def coerce_features(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [{"name": "Feature", "business_meaning": v}]
        return v


class FIEAgent:
    """
    Feature Intelligence Engine Agent.

    Reads GAL Sections 1–5 and uses domain-specific RAG to intelligently
    propose new derived features beneficial for machine learning models.
    """

    @staticmethod
    def _build_context(
        identity: DatasetIdentity,
        intent: UserIntentRecord | None,
        integrity: DataIntegrityRecord | None,
        findings: ExploratoryFindings | None,
        hypotheses: HypothesesRecord | None,
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
                "risk_tier": getattr(intent, 'risk_tier', 'TIER_3'),
            }
            sections.append(json.dumps(intent_summary, indent=2, default=str))

        # Section 3
        if integrity:
            sections.append("\n--- SECTION 3: DATA INTEGRITY RECORD ---")
            mod_count = len(integrity.modifications) if isinstance(integrity.modifications, list) else 0
            integrity_summary = {
                "validation_result": integrity.validation_result,
                "overall_reasoning": integrity.overall_reasoning,
                "modifications_count": mod_count,
            }
            sections.append(json.dumps(integrity_summary, indent=2, default=str))

        # Section 4
        if findings:
            sections.append("\n--- SECTION 4: EXPLORATORY FINDINGS ---")
            findings_data = {
                "distributions": findings.distributions,
                "correlations": findings.correlations,
                "anomalies": findings.anomalies,
                "target_associations": findings.target_associations,
                "overall_reasoning": findings.overall_reasoning,
            }
            sections.append(json.dumps(findings_data, indent=2, default=str))
            
        # Section 5
        if hypotheses:
            sections.append("\n--- SECTION 5: HYPOTHESES ---")
            hyp_list = hypotheses.hypotheses if isinstance(hypotheses.hypotheses, list) else []
            hypotheses_data = [
                {
                    "observation": h.observation_plain_language,
                    "hypothesis": h.hypothesis,
                    "plausibility": h.plausibility
                }
                for h in hyp_list
            ]
            sections.append(json.dumps(hypotheses_data, indent=2, default=str))

        return "\n".join(sections)

    @staticmethod
    def execute(
        identity: DatasetIdentity,
        findings: ExploratoryFindings | None = None,
        intent: UserIntentRecord | None = None,
        integrity: DataIntegrityRecord | None = None,
        hypotheses: HypothesesRecord | None = None,
        rules_mode: str = "full",
    ) -> FeaturePlanRecord:
        """
        Run the FIE agent: read GAL context, load domain RAG, invoke reasoning LLM,
        and return a validated FeaturePlanRecord for Section 6.
        """
        try:
            use_lite = rules_mode == "lite"
            rules = _load_rules(use_lite=use_lite)
            
            # Extract domain and risk_tier
            domain = identity.domain if identity and identity.domain else "UNKNOWN"
            risk_tier = getattr(intent, 'risk_tier', 'TIER_3') if intent else "TIER_3"

            # Load RAG Context
            rag_context = load_rag_context(domain, risk_tier)

            system_prompt = f"""You are EVA's Feature Intelligence Engine.
You MUST respond in English only.

{rules}

--- DOMAIN RAG CONTEXT ---
{rag_context if rag_context else "(No specific domain context found - rely on general feature engineering best practices.)"}
"""

            context = FIEAgent._build_context(identity, intent, integrity, findings, hypotheses)

            user_prompt = f"""Analyze the following GAL context and generate a domain-appropriate Feature Engineering Plan.

{context}

Generate features following the rules. Remember:
- Only create derived features using existing dataset columns.
- DO NOT hallucinate columns.
- Tie features back to user intent and hypotheses.
- Fill in EVERY field with specific, detailed content relevant to this dataset.
"""

            result = invoke_agent(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                pydantic_schema=FeatureOutput,
                model_type="reasoning",
            )

            # Filter out empty feature entries
            valid_features = []
            if isinstance(result.features, list):
                for f in result.features:
                    if isinstance(f, FeatureEntry) and f.name.strip():
                        valid_features.append(f)

            return FeaturePlanRecord(
                domain=result.domain,
                problem_type=result.problem_type,
                features=valid_features,
                overall_reasoning=result.overall_reasoning,
            )

        except Exception as e:
            raise Exception(f"FIE Agent execution failed: {str(e)}")
