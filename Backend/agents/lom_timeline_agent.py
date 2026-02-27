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

        system_prompt = f"""You are EVA's LOM Analysis agent.
You MUST respond in English only.

You MUST follow these LOM Timeline Rules:

{rules}

CRITICAL INSTRUCTION — DATA TYPE AWARENESS:
First, determine the nature of the uploaded data:
- If the data contains server logs, metrics, or observability data with timestamps and severity levels,
  build a chronological incident timeline and detect operational anomalies.
- If the data is structured JSON (e.g. metadata, records, configuration, educational content,
  business objects), adapt your analysis: instead of an "incident timeline", analyze the data
  structure, identify patterns, data quality issues, inconsistencies, or noteworthy observations
  across the records. Treat each record as an "event" in your timeline output.

NEVER report "no events found" as an anomaly. If the data is structured records, analyze what IS
there, not what is missing from a log-centric perspective."""

        # --- Build Timeline / Structural Analysis ---
        timeline_prompt = f"""Analyze the following data and produce a structured analysis.

If this is observability data (server logs, metrics), build a chronological event timeline
merging log events, metric anomalies, and code errors.

If this is structured data (JSON records, metadata, config files), create a structured analysis:
- Treat each record or data object as an "event" in your timeline output
- Use the record identifier or index as the timestamp field
- Analyze the structure, content patterns, and relationships between records
- Identify data quality issues, missing fields, duplicates, or inconsistencies

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
                overall_reasoning=f"Analysis failed: {str(e)}"
            )

        # --- Detect Anomalies / Data Issues ---
        anomaly_prompt = f"""Based on the following data and prior analysis, detect and classify issues.

If this is observability data, detect operational anomalies (error bursts, cascading failures,
resource exhaustion, etc.).

If this is structured data (JSON records, metadata), detect DATA QUALITY issues:
- Missing or inconsistent fields across records
- Outlier values or unexpected patterns
- Schema violations or structural inconsistencies
- Coverage gaps or classification issues
- Any noteworthy observations about the data content

{prior_context}

Prior analysis summary: {timeline.overall_reasoning if timeline else 'N/A'}
Records analyzed: {timeline.total_events if timeline else 0}

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
