import pandas as pd
from pathlib import Path
from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import DatasetIdentity

# Path to the rules file
RULES_PATH = Path(__file__).parent.parent / "rules" / "DomainAnalysisRules.lite.md"

def _load_rules() -> str:
    """Load the DomainAnalysisRules.md file for the DPSU Agent."""
    if RULES_PATH.exists():
        return RULES_PATH.read_text(encoding="utf-8")
    return "(No rules file found.)"

class DPSUAgent:
    """
    Dataset Profiler & Semantic Understanding Agent.
    Infers what the data means in the real world before doing any math.
    """
    
    @staticmethod
    def execute(dataframe: pd.DataFrame) -> DatasetIdentity:
        rules = _load_rules()
        system_prompt = f"""You are EVA's Dataset Profiler & Semantic Understanding (DPSU) module.
You MUST respond in English only.

You MUST follow these Domain Analysis Rules when making decisions:

{rules}

Your job is to look at a statistical summary of a dataset and infer its real-world identity.
What is the domain? What does a single row represent? What roles do columns play?
You are strictly observing and writing to the Global Analysis Ledger (GAL)."""
        
        # Build statistical summary string
        try:
            sample = dataframe.head(3).to_dict(orient="records")
            columns = dataframe.columns.tolist()
            dtypes = dataframe.dtypes.astype(str).to_dict()
            missing_pct = (dataframe.isnull().mean() * 100).round(1).to_dict()
            
            summary = f"""
            Columns: {columns}
            Data Types: {dtypes}
            Missing Value Percentages: {missing_pct}
            Sample Rows (3): {sample}
            """
            
            user_prompt = f"Analyze this dataset summary and infer its identity:\n{summary}"
            
            return invoke_agent(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                pydantic_schema=DatasetIdentity,
                model_type="reasoning"
            )
            
        except Exception as e:
            raise Exception(f"DPSU Agent execution failed: {str(e)}")
