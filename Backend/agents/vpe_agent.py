import json
import logging
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import (
    VisualizationEntry,
    VisualizationPlanRecord,
    DatasetIdentity,
    UserIntentRecord,
    ExploratoryFindings,
    HypothesesRecord,
    _coerce_to_list,
)
from Backend.storage.gal_manager import GALManager

RULES_PATH = Path(__file__).parent.parent / "rules" / "VPERules.md"
RULES_LITE_PATH = Path(__file__).parent.parent / "rules" / "VPERules.lite.md"


def _load_rules(use_lite: bool = False) -> str:
    path = RULES_LITE_PATH if use_lite else RULES_PATH
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No VPE rules file found — generate reasonable visualization plans.)"


# --- LLM-facing schema (what the Planner returns) ---
class VPEPlannerOutput(BaseModel):
    """What the LLM returns — a list of visualization plans."""
    visualizations: Optional[List[VisualizationEntry] | str] = Field(default_factory=list)
    total_planned: int = Field(default=0)
    overall_reasoning: str = Field(default="")

    @field_validator("visualizations", mode="before")
    @classmethod
    def coerce_visualizations(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [{"question": v}]
        return v


class VPEAgent:
    """
    Visualization Planner & Executor Agent.

    Two-stage architecture:
    1. Planner (LLM): Decides what to visualize and why
    2. Executor (Python/Plotly): Renders the actual charts
    """

    # ── Stage 1: Planner (LLM) ──

    @staticmethod
    def _build_context(
        identity: DatasetIdentity,
        intent: UserIntentRecord | None,
        findings: ExploratoryFindings,
        hypotheses: HypothesesRecord | None,
    ) -> str:
        sections = []

        sections.append("--- SECTION 1: DATASET IDENTITY ---")
        sections.append(identity.model_dump_json(indent=2))

        if intent:
            sections.append("\n--- SECTION 2: USER INTENT ---")
            intent_summary = {
                "primary_objective": intent.primary_objective,
                "selected_target": intent.selected_target,
                "analytical_goal": intent.analytical_goal,
                "stakeholder_type": intent.stakeholder_type,
                "deployment_mode": intent.deployment_mode,
            }
            sections.append(json.dumps(intent_summary, indent=2, default=str))

        sections.append("\n--- SECTION 4: EXPLORATORY FINDINGS ---")
        findings_data = {
            "distributions": findings.distributions,
            "correlations": findings.correlations,
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

        return "\n".join(sections)

    @staticmethod
    def plan(
        identity: DatasetIdentity,
        findings: ExploratoryFindings,
        intent: UserIntentRecord | None = None,
        hypotheses: HypothesesRecord | None = None,
        rules_mode: str = "full",
    ) -> VPEPlannerOutput:
        """Stage 1: LLM-driven planning — decides what to visualize."""
        use_lite = rules_mode == "lite"
        rules = _load_rules(use_lite=use_lite)

        system_prompt = f"""You are EVA's Visualization Planner.
You MUST respond in English only.

{rules}"""

        context = VPEAgent._build_context(identity, intent, findings, hypotheses)

        concrete_example = '''{
  "visualizations": [
    {
      "question": "How does survival rate differ across passenger classes?",
      "related_finding": "target_association_Pclass_Survived",
      "variables_used": ["Pclass", "Survived"],
      "chart_type": "bar",
      "chart_type_reasoning": "Group comparison of a categorical variable across discrete groups — bar chart makes magnitude differences immediately visible",
      "audience_calibration": "general",
      "interpretation": "First-class passengers survived at significantly higher rates than third-class passengers, confirming a class-based disparity in survival.",
      "confidence_note": "This is a correlation. The class-survival link may be driven by cabin location or evacuation access."
    },
    {
      "question": "Is the relationship between fare paid and survival linear?",
      "related_finding": "correlation_fare_survival",
      "variables_used": ["Fare", "Survived"],
      "chart_type": "box",
      "chart_type_reasoning": "Distribution comparison — box plot shows median, spread, and outliers for fare across survival groups",
      "audience_calibration": "general",
      "interpretation": "Survivors paid substantially higher fares on average, with a wider spread indicating both budget and premium travelers among survivors.",
      "confidence_note": "High fares correlate with first-class tickets, so this visual partially overlaps with the class-survival finding."
    }
  ],
  "total_planned": 2,
  "overall_reasoning": "Selected the two most impactful findings — class disparity and fare relationship — for visual confirmation of the core survival patterns."
}'''

        user_prompt = f"""Analyze the following GAL context and create a visualization plan.

{context}

Generate a visualization plan following your rules. Remember:
- Maximum 8 visualizations, focus on the most impactful
- EVERY chart must answer a specific question
- Include plain-language interpretations
- Choose chart types that match the data and question
- EVERY field must be filled with real content

Here is an EXAMPLE of the expected output format:
{concrete_example}

Now create YOUR visualization plan based on the actual data above. Fill in EVERY field with specific, detailed content relevant to this dataset."""

        result = invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=VPEPlannerOutput,
            model_type="reasoning",
        )

        logger.info("VPE Planner raw output: total_planned=%s, visualizations_count=%s",
                    result.total_planned, len(result.visualizations) if isinstance(result.visualizations, list) else 0)

        # Filter empty entries
        valid_vizs = []
        if isinstance(result.visualizations, list):
            for v in result.visualizations:
                if isinstance(v, VisualizationEntry) and v.question.strip():
                    valid_vizs.append(v)
                else:
                    logger.warning("VPE: Filtered out invalid visualization entry: %s", v)

        logger.info("VPE Planner: %d valid visualizations after filtering (from %d raw)",
                    len(valid_vizs), len(result.visualizations) if isinstance(result.visualizations, list) else 0)

        result.visualizations = valid_vizs
        result.total_planned = len(valid_vizs)
        return result

    # ── Stage 2: Executor (Plotly) ──

    @staticmethod
    def _create_chart(
        viz: VisualizationEntry,
        df: pd.DataFrame,
    ) -> Optional[Dict[str, Any]]:
        """Generate a Plotly figure from a visualization plan entry. Returns the figure as JSON dict."""
        try:
            variables = viz.variables_used if isinstance(viz.variables_used, list) else []
            # Filter to columns that actually exist in the dataframe
            available = [col for col in variables if col in df.columns]
            missing = [col for col in variables if col not in df.columns]

            if missing:
                logger.warning("VPE Chart '%s': columns %s not found in DataFrame (available: %s)",
                               viz.question[:50], missing, list(df.columns[:10]))

            if not available:
                logger.warning("VPE Chart '%s': no usable columns, skipping", viz.question[:50])
                return None

            chart_type = viz.chart_type.lower().strip()
            fig = None

            if chart_type in ("bar", "grouped_bar") and len(available) >= 1:
                if len(available) >= 2:
                    # Group comparison: x = categorical, color or y = target
                    x_col, y_col = available[0], available[1]
                    # If y is binary/categorical, do a count-based grouped bar
                    if df[y_col].nunique() <= 10:
                        grouped = df.groupby([x_col, y_col]).size().reset_index(name="count")
                        fig = px.bar(grouped, x=x_col, y="count", color=y_col,
                                     barmode="group", title=viz.question)
                    else:
                        agg = df.groupby(x_col)[y_col].mean().reset_index()
                        fig = px.bar(agg, x=x_col, y=y_col, title=viz.question)
                else:
                    counts = df[available[0]].value_counts().reset_index()
                    counts.columns = [available[0], "count"]
                    fig = px.bar(counts, x=available[0], y="count", title=viz.question)

            elif chart_type == "scatter" and len(available) >= 2:
                x_col, y_col = available[0], available[1]
                color_col = available[2] if len(available) >= 3 and df[available[2]].nunique() <= 10 else None
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                                 title=viz.question, opacity=0.7)

            elif chart_type == "histogram" and len(available) >= 1:
                color_col = available[1] if len(available) >= 2 and df[available[1]].nunique() <= 10 else None
                fig = px.histogram(df, x=available[0], color=color_col,
                                   title=viz.question, nbins=30, barmode="overlay",
                                   opacity=0.7)

            elif chart_type == "box" and len(available) >= 1:
                if len(available) >= 2:
                    fig = px.box(df, x=available[1], y=available[0], title=viz.question)
                else:
                    fig = px.box(df, y=available[0], title=viz.question)

            elif chart_type == "line" and len(available) >= 2:
                fig = px.line(df.sort_values(available[0]), x=available[0], y=available[1],
                              title=viz.question)

            elif chart_type == "heatmap":
                numeric_cols = [c for c in available if pd.api.types.is_numeric_dtype(df[c])]
                if len(numeric_cols) >= 2:
                    corr = df[numeric_cols].corr()
                    fig = px.imshow(corr, text_auto=".2f", title=viz.question,
                                   color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
                else:
                    return None

            elif chart_type == "pie" and len(available) >= 1:
                counts = df[available[0]].value_counts().reset_index()
                counts.columns = [available[0], "count"]
                fig = px.pie(counts, names=available[0], values="count", title=viz.question)

            else:
                # Fallback: try a bar chart for single variable
                if len(available) >= 1:
                    counts = df[available[0]].value_counts().reset_index()
                    counts.columns = [available[0], "count"]
                    fig = px.bar(counts, x=available[0], y="count", title=viz.question)
                else:
                    return None

            if fig is None:
                return None

            # Style the figure
            fig.update_layout(
                template="plotly_dark",
                font=dict(family="Inter, sans-serif", size=12),
                title_font_size=14,
                margin=dict(l=40, r=40, t=60, b=40),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
            )

            return json.loads(fig.to_json())

        except Exception as e:
            logger.error("VPE _create_chart failed for '%s': %s", viz.question[:50], e, exc_info=True)
            return None

    @staticmethod
    def execute(
        plan: VPEPlannerOutput,
        session_id: str,
        df: pd.DataFrame,
    ) -> VisualizationPlanRecord:
        """Stage 2: Execute the plan — render Plotly charts and build the GAL record."""
        viz_dir = Path("eva_sessions") / session_id / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)

        rendered_entries: List[VisualizationEntry] = []
        rendered_count = 0
        failed_count = 0

        for i, viz in enumerate(plan.visualizations):
            if not isinstance(viz, VisualizationEntry):
                continue

            plotly_json = VPEAgent._create_chart(viz, df)

            if plotly_json is not None:
                # Save chart as PNG for reference
                chart_filename = f"chart_{i+1}.png"
                chart_path = viz_dir / chart_filename
                try:
                    fig = go.Figure(plotly_json)
                    fig.write_image(str(chart_path), width=800, height=500, scale=2)
                    viz.chart_file_path = str(chart_path)
                except Exception:
                    viz.chart_file_path = None

                viz.plotly_config = plotly_json
                viz.validation_result = "passed"
                rendered_count += 1
            else:
                viz.validation_result = "failed"
                viz.plotly_config = None
                failed_count += 1

            rendered_entries.append(viz)

        return VisualizationPlanRecord(
            visualizations=rendered_entries,
            total_planned=plan.total_planned,
            total_rendered=rendered_count,
            total_failed=failed_count,
            overall_reasoning=plan.overall_reasoning,
        )

    # ── Fallback: Auto-generate basic charts ──

    @staticmethod
    def _auto_generate_plan(df: pd.DataFrame) -> VPEPlannerOutput:
        """Generate a basic visualization plan from DataFrame columns when LLM planner fails."""
        logger.info("VPE: Auto-generating fallback visualization plan from DataFrame columns")
        vizs: List[VisualizationEntry] = []

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

        # Distribution histograms for numeric columns (up to 4)
        for col in numeric_cols[:4]:
            vizs.append(VisualizationEntry(
                question=f"What is the distribution of {col}?",
                related_finding="auto_generated",
                variables_used=[col],
                chart_type="histogram",
                chart_type_reasoning=f"Histogram shows the frequency distribution of the numeric column '{col}'",
                audience_calibration="general",
                interpretation=f"Shows how values of '{col}' are distributed across the dataset.",
                confidence_note="Auto-generated fallback visualization.",
            ))

        # Value counts bar charts for categorical columns (up to 4)
        for col in categorical_cols[:4]:
            if df[col].nunique() <= 20:
                vizs.append(VisualizationEntry(
                    question=f"What are the most common values of {col}?",
                    related_finding="auto_generated",
                    variables_used=[col],
                    chart_type="bar",
                    chart_type_reasoning=f"Bar chart shows value counts for categorical column '{col}'",
                    audience_calibration="general",
                    interpretation=f"Shows the frequency of each category in '{col}'.",
                    confidence_note="Auto-generated fallback visualization.",
                ))

        # Correlation heatmap if enough numeric columns
        if len(numeric_cols) >= 3:
            vizs.append(VisualizationEntry(
                question="What are the correlations between numeric features?",
                related_finding="auto_generated",
                variables_used=numeric_cols[:8],
                chart_type="heatmap",
                chart_type_reasoning="Heatmap reveals pairwise correlations between numeric features",
                audience_calibration="general",
                interpretation="Shows pairwise linear correlations. Values near ±1 indicate strong relationships.",
                confidence_note="Auto-generated fallback visualization.",
            ))

        logger.info("VPE: Auto-generated %d fallback visualizations", len(vizs))
        return VPEPlannerOutput(
            visualizations=vizs,
            total_planned=len(vizs),
            overall_reasoning="Fallback plan: LLM planner returned no valid visualizations; auto-generated basic charts from dataset columns.",
        )

    # ── Full Pipeline Entry ──

    @staticmethod
    def run(
        identity: DatasetIdentity,
        findings: ExploratoryFindings,
        session_id: str,
        df: pd.DataFrame,
        intent: UserIntentRecord | None = None,
        hypotheses: HypothesesRecord | None = None,
        rules_mode: str = "full",
    ) -> VisualizationPlanRecord:
        """Full VPE pipeline: Plan (LLM) → Execute (Plotly)."""
        try:
            plan = VPEAgent.plan(
                identity=identity,
                findings=findings,
                intent=intent,
                hypotheses=hypotheses,
                rules_mode=rules_mode,
            )

            # Fallback: if LLM returned 0 valid visualizations, auto-generate
            if not plan.visualizations or len(plan.visualizations) == 0:
                logger.warning("VPE: LLM planner returned 0 visualizations, using fallback auto-generation")
                plan = VPEAgent._auto_generate_plan(df)

            record = VPEAgent.execute(
                plan=plan,
                session_id=session_id,
                df=df,
            )

            logger.info("VPE: Final result — %d rendered, %d failed",
                        record.total_rendered, record.total_failed)
            return record
        except Exception as e:
            logger.error("VPE Agent execution failed: %s", e, exc_info=True)
            raise Exception(f"VPE Agent execution failed: {str(e)}")
