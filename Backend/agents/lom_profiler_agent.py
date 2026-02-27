"""
LOM Profiler Agent — Profiles uploaded log/metric/code data.
Equivalent of DPSU for the LOM pipeline.
Writes Sections 2 (LogProfile) and 3 (MetricProfile) to LOM_GAL.
"""
from pathlib import Path
from Backend.agents.llm_core import invoke_agent
from Backend.agents.lom_parser import LOMParser, LOMDocument
from Backend.models.lom_schema import LogProfile, MetricProfile

RULES_DIR = Path(__file__).parent.parent / "rules"


def _load_rules() -> str:
    path = RULES_DIR / "LOMProfilerRules.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No LOM Profiler rules file found.)"


class LOMProfilerAgent:
    """Profiles observability data and writes log/metric profiles to the LOM_GAL."""

    @staticmethod
    def execute(lom_doc: LOMDocument) -> tuple:
        """
        Analyze parsed LOM data and return (LogProfile, MetricProfile).
        """
        rules = _load_rules()
        data_summary = LOMParser.build_llm_summary(lom_doc)

        system_prompt = f"""You are EVA's LOM Profiler agent.
You MUST respond in English only.

You MUST follow these LOM Profiler Rules:

{rules}

Your job is to analyze the parsed observability data summary and produce a structured profile.
You are strictly observing and writing to the LOM Analysis Ledger (LOM_GAL).
Do NOT hypothesize about root causes — only profile what you observe."""

        # --- Profile Logs ---
        log_profile = None
        if lom_doc.log_entries:
            log_prompt = f"""Analyze the following observability data and produce a LogProfile.
Focus on log level distribution, error rates, top error messages, and temporal patterns.

{data_summary}"""
            try:
                log_profile = invoke_agent(
                    system_prompt=system_prompt,
                    user_prompt=log_prompt,
                    pydantic_schema=LogProfile,
                    model_type="reasoning",
                )
            except Exception as e:
                log_profile = LogProfile(
                    overall_reasoning=f"LOM Profiler failed for log analysis: {str(e)}"
                )

        # --- Profile Metrics ---
        metric_profile = None
        if lom_doc.metric_points:
            metric_prompt = f"""Analyze the following observability data and produce a MetricProfile.
Focus on metric summaries, anomaly windows, and correlations with log events.

{data_summary}"""
            try:
                metric_profile = invoke_agent(
                    system_prompt=system_prompt,
                    user_prompt=metric_prompt,
                    pydantic_schema=MetricProfile,
                    model_type="reasoning",
                )
            except Exception as e:
                metric_profile = MetricProfile(
                    overall_reasoning=f"LOM Profiler failed for metric analysis: {str(e)}"
                )

        return log_profile, metric_profile
