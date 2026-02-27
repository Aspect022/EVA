"""
LOM Timeline Agent — Reconstructs chronological event timeline and detects anomalies.
Equivalent of EPR for the LOM pipeline.
Writes Sections 5 (TimelineReconstruction) and 6 (AnomalyFindings) to LOM_GAL.
"""
from pathlib import Path
from Backend.agents.llm_core import invoke_agent
from Backend.agents.lom_parser import LOMParser, LOMDocument
from Backend.models.lom_schema import (
    LogProfile, MetricProfile, CodeContext,
    TimelineReconstruction, AnomalyFindings,
)

RULES_DIR = Path(__file__).parent.parent / "rules"


def _load_rules() -> str:
    path = RULES_DIR / "LOMTimelineRules.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No LOM Timeline rules file found.)"


class LOMTimelineAgent:
    """Merges all data sources into a timeline and detects anomalies."""

    @staticmethod
    def execute(
        lom_doc: LOMDocument,
        log_profile: LogProfile = None,
        metric_profile: MetricProfile = None,
        code_context: CodeContext = None,
    ) -> tuple:
        """
        Build timeline and detect anomalies. Returns (TimelineReconstruction, AnomalyFindings).
        """
        rules = _load_rules()
        data_summary = LOMParser.build_llm_summary(lom_doc)

        # Build context from prior sections
        prior_context = ""
        if log_profile:
            prior_context += f"\n\n=== LOG PROFILE (Section 2) ===\n"
            prior_context += f"Total entries: {log_profile.total_entries}\n"
            prior_context += f"Error rate: {log_profile.error_rate_percent}%\n"
            prior_context += f"Temporal pattern: {log_profile.temporal_pattern}\n"
            if log_profile.error_burst_windows:
                prior_context += f"Error burst windows: {log_profile.error_burst_windows}\n"
            prior_context += f"Reasoning: {log_profile.overall_reasoning}\n"

        if metric_profile:
            prior_context += f"\n\n=== METRIC PROFILE (Section 3) ===\n"
            prior_context += f"Total data points: {metric_profile.total_data_points}\n"
            if metric_profile.anomaly_windows:
                prior_context += f"Anomaly windows: {metric_profile.anomaly_windows}\n"
            if metric_profile.metric_log_correlations:
                prior_context += f"Correlations: {metric_profile.metric_log_correlations}\n"
            prior_context += f"Reasoning: {metric_profile.overall_reasoning}\n"

        if code_context:
            prior_context += f"\n\n=== CODE CONTEXT (Section 4) ===\n"
            for a in code_context.artifacts:
                prior_context += f"File: {a.filename} ({a.language})\n"
                if a.traceback:
                    prior_context += f"Traceback: {a.traceback[:500]}\n"
                if a.error_type:
                    prior_context += f"Error: {a.error_type}: {a.error_message}\n"

        system_prompt = f"""You are EVA's LOM Timeline Reconstruction agent.
You MUST respond in English only.

You MUST follow these LOM Timeline Rules:

{rules}

Your job is to merge all observability data into a chronological timeline and detect anomalies.
Do NOT hypothesize about root causes — describe WHAT happened and WHEN."""

        # --- Build Timeline ---
        timeline_prompt = f"""Build a chronological event timeline from the following observability data.
Merge log events, metric anomalies, and code errors into a single ordered narrative.

{prior_context}

{data_summary}"""

        try:
            timeline = invoke_agent(
                system_prompt=system_prompt,
                user_prompt=timeline_prompt,
                pydantic_schema=TimelineReconstruction,
                model_type="reasoning",
            )
        except Exception as e:
            timeline = TimelineReconstruction(
                overall_reasoning=f"Timeline reconstruction failed: {str(e)}"
            )

        # --- Detect Anomalies ---
        anomaly_prompt = f"""Based on the following observability data and timeline analysis, detect and classify all anomalies.

{prior_context}

Timeline cascade pattern: {timeline.cascade_pattern if timeline else 'N/A'}
Timeline event count: {timeline.total_events if timeline else 0}

{data_summary}"""

        try:
            anomalies = invoke_agent(
                system_prompt=system_prompt,
                user_prompt=anomaly_prompt,
                pydantic_schema=AnomalyFindings,
                model_type="reasoning",
            )
        except Exception as e:
            anomalies = AnomalyFindings(
                overall_reasoning=f"Anomaly detection failed: {str(e)}"
            )

        return timeline, anomalies
