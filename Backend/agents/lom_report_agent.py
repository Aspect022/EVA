"""
LOM Report Agent — Generates final RCA narrative report.
Equivalent of RG for the LOM pipeline.
Writes Section 8 (RCAReport) to LOM_GAL.
"""
from pathlib import Path
from Backend.agents.llm_core import invoke_agent
from Backend.models.lom_schema import LOMAnalysisLedger, RCAReport

RULES_DIR = Path(__file__).parent.parent / "rules"


def _load_rules() -> str:
    path = RULES_DIR / "LOMReportRules.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No LOM Report rules file found.)"


class LOMReportAgent:
    """Compiles all LOM_GAL sections into a human-readable RCA report."""

    @staticmethod
    def execute(ledger: LOMAnalysisLedger) -> RCAReport:
        """Generate the final RCA report narrative."""
        rules = _load_rules()

        # Build input context from all sections
        context_parts = []

        # Source inventory
        if ledger.source_inventory:
            context_parts.append(f"=== SOURCE INVENTORY ===")
            context_parts.append(f"Total files analyzed: {ledger.source_inventory.total_files}")
            context_parts.append(f"Log entries: {ledger.source_inventory.total_log_entries}")
            context_parts.append(f"Metric points: {ledger.source_inventory.total_metric_points}")
            context_parts.append(f"Code artifacts: {ledger.source_inventory.total_code_artifacts}")
            if ledger.source_inventory.overall_time_range_start:
                context_parts.append(f"Analysis period: {ledger.source_inventory.overall_time_range_start} to {ledger.source_inventory.overall_time_range_end}")

        # Log profile
        if ledger.log_profile:
            context_parts.append(f"\n=== LOG PROFILE ===")
            context_parts.append(f"Error rate: {ledger.log_profile.error_rate_percent}%")
            context_parts.append(f"Top errors: {[e.message[:100] for e in ledger.log_profile.top_error_messages[:5]] if ledger.log_profile.top_error_messages else 'None'}")
            context_parts.append(f"Temporal pattern: {ledger.log_profile.temporal_pattern}")

        # Metric profile
        if ledger.metric_profile:
            context_parts.append(f"\n=== METRIC PROFILE ===")
            if ledger.metric_profile.anomaly_windows:
                context_parts.append(f"Anomaly windows: {ledger.metric_profile.anomaly_windows}")
            if ledger.metric_profile.metric_log_correlations:
                context_parts.append(f"Correlations: {ledger.metric_profile.metric_log_correlations}")

        # Timeline
        if ledger.timeline:
            context_parts.append(f"\n=== INCIDENT TIMELINE ===")
            if ledger.timeline.incident_window_start:
                context_parts.append(f"Incident period: {ledger.timeline.incident_window_start} to {ledger.timeline.incident_window_end}")
            context_parts.append(f"Cascade pattern: {ledger.timeline.cascade_pattern}")
            if ledger.timeline.events:
                context_parts.append("Key events:")
                for e in ledger.timeline.events[:30]:
                    context_parts.append(f"  [{e.timestamp}] {e.severity} ({e.source}): {e.description[:150]}")
            context_parts.append(f"Timeline reasoning: {ledger.timeline.overall_reasoning}")

        # Anomaly findings
        if ledger.anomaly_findings:
            context_parts.append(f"\n=== ANOMALY FINDINGS ===")
            context_parts.append(f"Total anomalies: {ledger.anomaly_findings.total_anomalies}, Critical: {ledger.anomaly_findings.critical_count}")
            if ledger.anomaly_findings.anomalies:
                for a in ledger.anomaly_findings.anomalies:
                    context_parts.append(f"  [{a.severity}] {a.anomaly_type}: {a.description}")

        # RCA Hypotheses
        if ledger.rca_hypotheses:
            context_parts.append(f"\n=== RCA HYPOTHESES ===")
            context_parts.append(f"Primary suspect: {ledger.rca_hypotheses.primary_suspect}")
            if ledger.rca_hypotheses.hypotheses:
                for h in ledger.rca_hypotheses.hypotheses:
                    context_parts.append(f"\nHypothesis [{h.plausibility}]: {h.hypothesis}")
                    context_parts.append(f"  Category: {h.category}")
                    context_parts.append(f"  Supporting evidence: {h.supporting_evidence}")
                    if h.five_whys:
                        context_parts.append(f"  5-Whys: {h.five_whys}")
                    context_parts.append(f"  Reasoning: {h.reasoning}")
            context_parts.append(f"Overall reasoning: {ledger.rca_hypotheses.overall_reasoning}")

        full_context = "\n".join(context_parts)

        system_prompt = f"""You are EVA's LOM Report Generator.
You MUST respond in English only.

You MUST follow these LOM Report Rules:

{rules}

CRITICAL INSTRUCTION — DATA TYPE AWARENESS:
Determine the nature of the analyzed data from the context below:
- If the data involved observability/infrastructure data (server logs, metrics, incidents),
  generate a traditional Root Cause Analysis report with incident timeline, root cause,
  affected services, and remediation steps.
- If the data involved structured data (JSON records, metadata, educational content, etc.),
  generate a DATA ANALYSIS report: executive summary of findings, data quality assessment,
  key patterns and insights, recommendations for improvement.

Adapt your report format to match the actual data content."""

        user_prompt = f"""Generate a comprehensive analysis report from the following data.

For observability data: include executive summary, root cause, incident timeline,
affected services, impact assessment, remediation steps, and prevention recommendations.

For structured data: include executive summary of findings, data structure analysis,
quality assessment, key insights, anomalies or issues found, and recommendations.

{full_context}"""

        try:
            return invoke_agent(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                pydantic_schema=RCAReport,
                model_type="reasoning",
            )
        except Exception as e:
            return RCAReport(
                executive_summary=f"Report generation failed: {str(e)}",
                confidence_level="Low",
            )
