"""
LOM RCA Agent — Root Cause Analysis hypothesis generation.
Equivalent of IHE for the LOM pipeline.
Writes Section 7 (RCAHypotheses) to LOM_GAL.
"""
from pathlib import Path
from Backend.agents.llm_core import invoke_agent
from Backend.models.lom_schema import (
    LOMAnalysisLedger, RCAHypotheses,
)

RULES_DIR = Path(__file__).parent.parent / "rules"


def _load_rules() -> str:
    path = RULES_DIR / "LOMRCARules.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No LOM RCA rules file found.)"


class LOMRCAAgent:
    """Generates root cause hypotheses with evidence chains."""

    @staticmethod
    def execute(ledger: LOMAnalysisLedger) -> RCAHypotheses:
        """
        Analyze all LOM_GAL sections and generate RCA hypotheses.
        """
        rules = _load_rules()

        # Build comprehensive context from all prior sections
        context_parts = []

        if ledger.source_inventory:
            context_parts.append(f"=== SOURCE INVENTORY (Section 1) ===")
            context_parts.append(f"Files: {ledger.source_inventory.total_files}")
            context_parts.append(f"Log entries: {ledger.source_inventory.total_log_entries}")
            context_parts.append(f"Metric points: {ledger.source_inventory.total_metric_points}")
            context_parts.append(f"Code artifacts: {ledger.source_inventory.total_code_artifacts}")
            if ledger.source_inventory.overall_time_range_start:
                context_parts.append(f"Time range: {ledger.source_inventory.overall_time_range_start} to {ledger.source_inventory.overall_time_range_end}")

        if ledger.log_profile:
            context_parts.append(f"\n=== LOG PROFILE (Section 2) ===")
            context_parts.append(f"Total entries: {ledger.log_profile.total_entries}")
            context_parts.append(f"Error rate: {ledger.log_profile.error_rate_percent}%")
            context_parts.append(f"Unique sources: {ledger.log_profile.unique_sources}")
            if ledger.log_profile.top_error_messages:
                context_parts.append("Top errors:")
                for err in ledger.log_profile.top_error_messages[:5]:
                    context_parts.append(f"  - [{err.count}x] {err.message[:200]} (source: {err.source})")
            if ledger.log_profile.error_burst_windows:
                context_parts.append(f"Error burst windows: {ledger.log_profile.error_burst_windows}")
            context_parts.append(f"Temporal pattern: {ledger.log_profile.temporal_pattern}")
            context_parts.append(f"Reasoning: {ledger.log_profile.overall_reasoning}")

        if ledger.metric_profile:
            context_parts.append(f"\n=== METRIC PROFILE (Section 3) ===")
            context_parts.append(f"Total data points: {ledger.metric_profile.total_data_points}")
            if ledger.metric_profile.metrics:
                context_parts.append("Metrics:")
                for m in ledger.metric_profile.metrics[:10]:
                    context_parts.append(f"  - {m.metric_name}: min={m.min_value}, max={m.max_value}, mean={m.mean_value}, anomalies={m.anomaly_count}")
            if ledger.metric_profile.anomaly_windows:
                context_parts.append(f"Anomaly windows: {ledger.metric_profile.anomaly_windows}")
            if ledger.metric_profile.metric_log_correlations:
                context_parts.append(f"Metric-Log correlations: {ledger.metric_profile.metric_log_correlations}")
            context_parts.append(f"Reasoning: {ledger.metric_profile.overall_reasoning}")

        if ledger.code_context:
            context_parts.append(f"\n=== CODE CONTEXT (Section 4) ===")
            for a in ledger.code_context.artifacts:
                context_parts.append(f"File: {a.filename} ({a.language})")
                if a.traceback:
                    context_parts.append(f"Traceback: {a.traceback[:800]}")
                if a.error_type:
                    context_parts.append(f"Error: {a.error_type}: {a.error_message}")
            if ledger.code_context.traceback_chains:
                context_parts.append(f"Traceback chains: {ledger.code_context.traceback_chains}")

        if ledger.timeline:
            context_parts.append(f"\n=== TIMELINE (Section 5) ===")
            context_parts.append(f"Total events: {ledger.timeline.total_events}")
            if ledger.timeline.incident_window_start:
                context_parts.append(f"Incident window: {ledger.timeline.incident_window_start} to {ledger.timeline.incident_window_end}")
            if ledger.timeline.cascade_pattern:
                context_parts.append(f"Cascade pattern: {ledger.timeline.cascade_pattern}")
            if ledger.timeline.events:
                context_parts.append("Key events:")
                for e in ledger.timeline.events[:20]:
                    context_parts.append(f"  [{e.timestamp}] {e.severity} ({e.event_type}, {e.source}): {e.description[:200]}")
            context_parts.append(f"Reasoning: {ledger.timeline.overall_reasoning}")

        if ledger.anomaly_findings:
            context_parts.append(f"\n=== ANOMALY FINDINGS (Section 6) ===")
            context_parts.append(f"Total anomalies: {ledger.anomaly_findings.total_anomalies}")
            context_parts.append(f"Critical count: {ledger.anomaly_findings.critical_count}")
            if ledger.anomaly_findings.anomalies:
                for a in ledger.anomaly_findings.anomalies:
                    context_parts.append(f"  [{a.severity}] {a.anomaly_type}: {a.description}")
                    if a.affected_components:
                        context_parts.append(f"    Affected: {a.affected_components}")
            context_parts.append(f"Reasoning: {ledger.anomaly_findings.overall_reasoning}")

        full_context = "\n".join(context_parts)

        system_prompt = f"""You are EVA's LOM Root Cause Analysis agent.
You MUST respond in English only.

You MUST follow these LOM RCA Rules:

{rules}

CRITICAL INSTRUCTION — DATA TYPE AWARENESS:
First, determine the nature of the data from the context below:
- If the data is observability/infrastructure data (server logs, metrics, alerts), generate
  traditional root cause hypotheses about system failures, incidents, and cascading errors.
- If the data is structured data (e.g. JSON records, metadata, educational content, business
  objects), generate analytical hypotheses about DATA QUALITY issues, structural problems,
  coverage gaps, or improvement opportunities found in the data.

NEVER produce hypotheses about "failed data extraction" or "pipeline malfunction". Analyze
the ACTUAL CONTENT of the uploaded data, whatever it may be."""

        user_prompt = f"""Analyze the following data analysis results and generate hypotheses.

For observability data: build evidence chains linking log errors -> metric anomalies -> code
locations -> potential root causes.

For structured data: build hypotheses about data quality, completeness, consistency, and
potential issues. Each hypothesis should identify a specific finding in the data with
supporting evidence from the analysis.

{full_context}"""

        try:
            return invoke_agent(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                pydantic_schema=RCAHypotheses,
                model_type="reasoning",
            )
        except Exception as e:
            return RCAHypotheses(
                overall_reasoning=f"RCA hypothesis generation failed: {str(e)}"
            )
