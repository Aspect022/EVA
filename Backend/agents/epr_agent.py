import math
import json
import re
import pandas as pd
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional

from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import (
    ExploratoryFindings,
    DatasetIdentity,
    UserIntentRecord,
    ScriptExecution,
    _coerce_to_list,
    _coerce_to_dict,
)
from Backend.tools.executor import CodeExecutor

# Path to the rules file
RULES_PATH = Path(__file__).parent.parent / "rules" / "DataScienceRules.md"


def _load_rules() -> str:
    """Load the DataScienceRules.md file for the Strategy Agent."""
    if RULES_PATH.exists():
        return RULES_PATH.read_text(encoding="utf-8")
    return "(No rules file found — use conservative defaults.)"


# --- LLM-facing schema (no script_execution) ---
class ExplorationInterpretation(BaseModel):
    """What the Interpretation Agent returns — semantic meaning, no execution metadata."""
    distributions: Optional[Dict[str, Any] | str] = Field(default_factory=dict)
    correlations: Optional[List[Any] | str] = Field(default_factory=list)
    anomalies: Optional[List[str] | str] = Field(default_factory=list)
    target_associations: Optional[Dict[str, Any] | str] = Field(default_factory=dict)
    overall_reasoning: str = Field(default="")

    @field_validator("correlations", "anomalies", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)

    @field_validator("distributions", "target_associations", mode="before")
    @classmethod
    def coerce_dicts(cls, v):
        return _coerce_to_dict(v)


class EPRAgent:
    """
    Exploration & Pattern Recognition Agent.

    Three-step architecture:
      1. Code Writer    — generates a Python stats script (guided by rules)
      2. CodeExecutor   — runs it, captures JSON output
      3. Interpreter    — LLM reads raw results + rules → adds semantic meaning
    """

    @staticmethod
    def _generate_exploration_script(
        dataframe: pd.DataFrame,
        identity: DatasetIdentity,
        intent: UserIntentRecord | None,
        input_path: str,
        output_json_path: str,
    ) -> str:
        rules = _load_rules()

        intent_context = ""
        if intent:
            intent_context = (
                f"\nUser Intent:\n"
                f"  Goal: {intent.primary_objective}\n"
                f"  Target: {intent.selected_target or 'none selected'}\n"
            )

        columns = dataframe.columns.tolist()
        dtypes = dataframe.dtypes.astype(str).to_dict()
        shape = dataframe.shape

        prompt = f"""Write a COMPLETE, RUNNABLE Python script that performs exploratory data analysis.

Follow these data science principles:
{rules}

RULES FOR THE SCRIPT:
1. Read the dataset path from the environment variable: `os.environ["EVA_INPUT_PATH"]`
2. Save results as a JSON file to the environment variable: `os.environ["EVA_OUTPUT_PATH"]`
3. The JSON must have these top-level keys:
   - "distributions": dict of column_name -> {{mean, median, std, min, max, skew, unique_count}}
   - "correlations": list of dicts {{col_a, col_b, correlation, strength}} for top correlations
   - "anomalies": list of strings describing any unusual patterns found
   - "target_associations": dict of column_name -> association_strength (if a target exists)
4. Use pandas and scipy.stats where helpful.
5. For correlations, only include pairs with |r| > 0.3.
6. For anomalies, check for: extreme skewness (>2), high cardinality categoricals,
   constant columns, and outliers beyond 3 IQRs.
7. Handle NaN/Inf values — replace them with None before writing JSON.
8. Print a brief summary of findings while running.
9. Wrap everything in a main() function and call it at the bottom.
10. The script must be completely self-contained. Only use pandas, numpy, scipy, json, os.

Dataset Context:
  Domain: {identity.domain}
  Row Meaning: {identity.row_meaning or 'unknown'}
  Columns: {columns}
  Types: {dtypes}
  Shape: {shape}
{intent_context}
Respond with ONLY the Python script. No markdown, no explanation."""

        result = invoke_agent(
            system_prompt="You are an expert Python data scientist. You MUST respond in English only. Output ONLY executable Python code. No markdown, no explanation, just code.",
            user_prompt=prompt,
        )

        code = result.content if hasattr(result, "content") else str(result)
        code = re.sub(r"^```(?:python)?\s*", "", code, flags=re.MULTILINE)
        code = re.sub(r"```\s*$", "", code, flags=re.MULTILINE)
        return code.strip()

    @staticmethod
    def _interpret_findings(
        findings_json: dict, identity: DatasetIdentity, intent: UserIntentRecord | None
    ) -> ExplorationInterpretation:
        """LLM reads raw statistics + rules → adds semantic interpretation with WHY."""
        rules = _load_rules()

        intent_block = ""
        if intent:
            intent_block = (
                f"\n--- USER INTENT ---\n"
                f"Goal: {intent.primary_objective}\n"
                f"Target: {intent.selected_target or 'none selected'}\n"
            )

        system_prompt = f"""You are EVA's Exploration & Pattern Recognition Interpreter.
You MUST respond in English only.
Keep your response concise. Do NOT repeat raw data values in your output.

Follow these data science principles:
{rules}

Your job:
1. Read the statistical metrics computed from the dataset.
2. Interpret their REAL-WORLD meaning based on the domain context.
3. Explain WHY each pattern matters for this specific analysis goal.
4. Identify anomalies and correlations that could impact downstream decisions.
5. Provide an overall_reasoning field with your high-level interpretation."""

        user_prompt = (
            f"--- DATASET IDENTITY ---\n{identity.model_dump_json(indent=2)}\n"
            f"{intent_block}\n"
            f"--- STATISTICAL FINDINGS ---\n{json.dumps(findings_json, indent=2, default=str)}"
        )

        return invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=ExplorationInterpretation,
        )

    @staticmethod
    def _sanitize_for_json(obj):
        """Replace NaN/Inf values with None so the output is JSON-serializable."""
        if isinstance(obj, dict):
            return {k: EPRAgent._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [EPRAgent._sanitize_for_json(v) for v in obj]
        elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj

    @staticmethod
    def execute(
        dataframe: pd.DataFrame,
        identity: DatasetIdentity,
        session_id: str,
        csv_file_name: str,
        intent: UserIntentRecord | None = None,
    ) -> ExploratoryFindings:
        try:
            from Backend.storage.gal_manager import GALManager

            repaired_path = (GALManager.get_dataset_path(session_id, "repaired_dataset") / csv_file_name).resolve()
            snapshot_path = (GALManager.get_dataset_path(session_id, "dataset_snapshot") / csv_file_name).resolve()
            input_path = str(repaired_path if repaired_path.exists() else snapshot_path)

            output_json_path = str(
                (GALManager.get_dataset_path(session_id, "scripts") / "epr_results.json").resolve()
            )

            # 1. Generate and execute the exploration script
            script_code = EPRAgent._generate_exploration_script(
                dataframe, identity, intent, input_path, output_json_path
            )

            exec_result = CodeExecutor.execute(
                session_id=session_id,
                script_content=script_code,
                input_csv_path=input_path,
                output_csv_path=output_json_path,
                script_name="epr_exploration.py",
            )

            script_execution = ScriptExecution(
                script_path=exec_result.script_path,
                exit_code=exec_result.exit_code,
                stdout=exec_result.stdout[:2000],
                stderr=exec_result.stderr[:2000],
                success=exec_result.success,
            )

            # 2. Load the script-generated JSON results
            findings_json = {}
            if exec_result.success and Path(output_json_path).exists():
                with open(output_json_path, "r", encoding="utf-8") as f:
                    findings_json = json.load(f)
                findings_json = EPRAgent._sanitize_for_json(findings_json)

            # 3. Interpret with rules + intent (clean model, no ScriptExecution)
            if findings_json:
                interpretation = EPRAgent._interpret_findings(findings_json, identity, intent)
            else:
                desc = dataframe.describe(include="all").to_dict()
                numeric_df = dataframe.select_dtypes(include=["float64", "int64"])
                corr = numeric_df.corr().to_dict() if not numeric_df.empty else {}
                fallback = {
                    "distributions": EPRAgent._sanitize_for_json(desc),
                    "correlations": [{"matrix": EPRAgent._sanitize_for_json(corr)}],
                }
                interpretation = EPRAgent._interpret_findings(fallback, identity, intent)

            # 4. Assemble final GAL record (Python-only)
            findings = ExploratoryFindings(
                distributions=interpretation.distributions,
                correlations=interpretation.correlations,
                anomalies=interpretation.anomalies,
                target_associations=interpretation.target_associations,
                overall_reasoning=interpretation.overall_reasoning,
                script_execution=script_execution,
            )

            # Override with raw computed data from the script
            if findings_json:
                if "distributions" in findings_json:
                    findings.distributions = findings_json["distributions"]
                raw_corr = findings_json.get("correlations", [])
                if raw_corr:
                    findings.correlations = raw_corr if isinstance(raw_corr, list) else [raw_corr]
                if "target_associations" in findings_json:
                    findings.target_associations = findings_json["target_associations"]

            return findings

        except Exception as e:
            raise Exception(f"EPR Agent execution failed: {str(e)}")
