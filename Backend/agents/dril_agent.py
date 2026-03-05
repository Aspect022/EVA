import re
import pandas as pd
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import (
    DataIntegrityRecord,
    DatasetIdentity,
    UserIntentRecord,
    ScriptExecution,
    ModificationRecord,
)
from Backend.tools.executor import CodeExecutor

# Path to the rules files
RULES_DIR = Path(__file__).parent.parent / "rules"


def _load_rules(rules_mode: str = "full") -> str:
    """Load the DataScienceRules file for the Strategy Agent."""
    filename = "DataScienceRules.lite.md" if rules_mode == "lite" else "DataScienceRules.md"
    path = RULES_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No rules file found — use conservative defaults.)"


# --- LLM-facing schema (clean, no script_execution) ---
class CleaningStrategy(BaseModel):
    """What the Strategy Agent returns — reasoning + decisions, no code."""
    modifications: List[ModificationRecord] = Field(default_factory=list)
    restricted_columns: Dict[str, Any] = Field(
        default_factory=dict, description="Columns flagged as restricted and why"
    )
    validation_result: str = Field(
        default="pending", description="Overall assessment of data quality"
    )
    overall_reasoning: str = Field(
        default="", description="High-level explanation of the cleaning approach and WHY these decisions were made"
    )


class DRILAgent:
    """
    Data Repair & Integrity Layer Agent.

    Three-step architecture:
      1. Strategy Agent  — reads GAL + DataScienceRules → decides WHAT to fix and WHY
      2. Code Writer     — takes the strategy → writes a runnable Python script
      3. CodeExecutor    — runs the script → captures results
    """

    # ------------------------------------------------------------------
    # Step 1: Strategy Agent — reads rules + data → reasons
    # ------------------------------------------------------------------
    @staticmethod
    def _propose_strategy(
        dataframe_summary: str,
        identity: DatasetIdentity,
        intent: UserIntentRecord | None,
        rules_mode: str = "full",
    ) -> CleaningStrategy:
        rules = _load_rules(rules_mode)

        intent_block = ""
        if intent:
            intent_block = (
                f"\n--- USER INTENT ---\n"
                f"Goal: {intent.analytical_goal}\n"
                f"Target Variable: {intent.selected_target or 'none selected'}\n"
                f"Interpretability: {intent.interpretability_priority}\n"
                f"Decision Supported: {intent.decision_supported}\n"
            )

        system_prompt = f"""You are EVA's Data Repair Strategy Agent.

You MUST follow these Data Science Rules when making decisions:

{rules}

Your job:
1. Analyze the data quality issues in the provided summary.
2. For EACH problem, document:
   - What the problem is
   - WHY it matters for this specific dataset and analysis goal
   - What fix to apply (following the rules above)
   - What alternatives you considered and rejected
3. Provide an overall_reasoning field explaining your high-level approach.

Be specific. Cite which rule number informed each decision."""

        user_prompt = (
            f"--- DATASET IDENTITY ---\n{identity.model_dump_json(indent=2)}\n"
            f"{intent_block}\n"
            f"--- DATA SUMMARY ---\n{dataframe_summary}"
        )

        return invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=CleaningStrategy,
            model_type="reasoning"
        )

    # ------------------------------------------------------------------
    # Step 2: Code Writer — takes strategy → writes Python
    # ------------------------------------------------------------------
    @staticmethod
    def _write_repair_code(
        strategy: CleaningStrategy,
        identity: DatasetIdentity,
        dataframe_summary: str,
        input_path: str,
        output_path: str,
    ) -> str:
        strategy_instructions = "\n".join(
            f"- Column/Issue: {m.problem} → Fix: {m.strategy_chosen} (Reason: {m.impact})"
            for m in strategy.modifications
        )

        prompt = f"""Write a COMPLETE, RUNNABLE Python script that cleans a CSV dataset.

INPUT FILE:  Read from `os.environ["EVA_INPUT_PATH"]`
OUTPUT FILE: Write to `os.environ["EVA_OUTPUT_PATH"]`

CLEANING STRATEGY (follow these decisions exactly):
{strategy_instructions}

Overall approach: {strategy.overall_reasoning}

RULES:
1. Read from the environment variable `EVA_INPUT_PATH`, save cleaned result to the environment variable `EVA_OUTPUT_PATH`.
2. Use pandas for all operations.
3. Use proper imputation: median for numeric (or KNN if specified), mode for categorical.
4. Print a brief summary of EVERY change (column, action, rows affected).
5. Wrap everything in a main() function and call it at the bottom.
6. Only use pandas, sklearn, and os. No external APIs.
7. The script must be COMPLETELY self-contained.

Data Profile:
{dataframe_summary}

Respond with ONLY pure Python code. No markdown fences, no explanation."""

        result = invoke_agent(
            system_prompt="You are an expert Python data engineer. Output ONLY executable Python code. No markdown, no explanation, just code.",
            user_prompt=prompt,
            model_type="coder"
        )

        code = result.content if hasattr(result, "content") else str(result)
        code = re.sub(r"^```(?:python)?\s*", "", code, flags=re.MULTILINE)
        code = re.sub(r"```\s*$", "", code, flags=re.MULTILINE)
        return code.strip()

    # ------------------------------------------------------------------
    # Step 3: Orchestrate — strategy → code → execute → assemble GAL
    # ------------------------------------------------------------------
    @staticmethod
    def execute(
        dataframe: pd.DataFrame,
        identity: DatasetIdentity,
        session_id: str,
        csv_file_name: str,
        intent: UserIntentRecord | None = None,
        rules_mode: str = "full",
    ) -> tuple[pd.DataFrame, DataIntegrityRecord]:
        try:
            from Backend.storage.gal_manager import GALManager

            input_path = str(
                (GALManager.get_dataset_path(session_id, "dataset_snapshot") / csv_file_name).resolve()
            )
            output_path = str(
                (GALManager.get_dataset_path(session_id, "repaired_dataset") / csv_file_name).resolve()
            )

            # Build data summary
            missing_pct = (dataframe.isnull().mean() * 100).round(1).to_dict()
            dtypes = dataframe.dtypes.astype(str).to_dict()
            summary = f"Shape: {dataframe.shape}\nMissingness: {missing_pct}\nTypes: {dtypes}"

            # 1. Strategy Agent — reason with rules + GAL context
            strategy = DRILAgent._propose_strategy(summary, identity, intent, rules_mode)

            # 2. Code Writer — generate the script from strategy
            script_code = DRILAgent._write_repair_code(
                strategy, identity, summary, input_path, output_path
            )

            # 3. Execute
            exec_result = CodeExecutor.execute(
                session_id=session_id,
                script_content=script_code,
                input_csv_path=input_path,
                output_csv_path=output_path,
                script_name="dril_repair.py",
            )

            # 4. Assemble GAL record (Python-only, LLM never touches this)
            integrity_record = DataIntegrityRecord(
                modifications=strategy.modifications,
                restricted_columns=strategy.restricted_columns,
                overall_reasoning=strategy.overall_reasoning,
                validation_result=(
                    "script_executed_successfully"
                    if exec_result.success
                    else f"script_failed: {exec_result.stderr[:500]}"
                ),
                script_execution=ScriptExecution(
                    script_path=exec_result.script_path,
                    exit_code=exec_result.exit_code,
                    stdout=exec_result.stdout[:2000],
                    stderr=exec_result.stderr[:2000],
                    success=exec_result.success,
                ),
            )

            # 5. Load repaired data or fallback
            if exec_result.success:
                repaired_df = pd.read_csv(output_path)
            else:
                repaired_df = dataframe.copy()

            return repaired_df, integrity_record

        except Exception as e:
            raise Exception(f"DRIL Agent execution failed: {str(e)}")
