import pandas as pd
from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import DataIntegrityRecord, DatasetIdentity

class DRILAgent:
    """
    Data Repair & Integrity Layer Agent.
    Autonomously handles missing values and formats, driven by the semantic meaning established during profiling.
    """
    
    @staticmethod
    def _propose_cleaning_strategy(dataframe_summary: str, identity: DatasetIdentity) -> DataIntegrityRecord:
        system_prompt = """You are EVA's Data Repair & Integrity Layer (DRIL).
        Your job is to propose a cleaning strategy for missing values and bad types based on the REAL-WORLD meaning of the columns.
        Do not drop highly restricted columns without extremely high confidence.
        Output your proposed modification record."""
        
        user_prompt = f"""
        Identity Context:\n{identity.model_dump_json(indent=2)}
        Data Summary:\n{dataframe_summary}
        """
        
        return invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=DataIntegrityRecord
        )

    @staticmethod
    def execute(dataframe: pd.DataFrame, identity: DatasetIdentity) -> tuple[pd.DataFrame, DataIntegrityRecord]:
        try:
            # 1. Summarize missingness and types
            missing_pct = (dataframe.isnull().mean() * 100).round(1).to_dict()
            dtypes = dataframe.dtypes.astype(str).to_dict()
            summary = f"Missingness: {missing_pct}\nTypes: {dtypes}"
            
            # 2. Get LLM approval for strategy
            integrity_record = DRILAgent._propose_cleaning_strategy(summary, identity)
            
            # 3. Apply standard, highly conversative Pandas cleaning for Phase 1
            # In a real system the LLM would output executable python actions. For stability in Phase 1:
            # - Drop columns missing > 60%
            # - Median fill numerical
            # - Mode fill categorical
            
            repaired_df = dataframe.copy()
            for col in repaired_df.columns:
                if missing_pct[col] > 60.0:
                    repaired_df.drop(columns=[col], inplace=True)
                elif repaired_df[col].dtype in ['float64', 'int64'] and repaired_df[col].isnull().any():
                    repaired_df[col].fillna(repaired_df[col].median(), inplace=True)
                elif repaired_df[col].dtypes == 'object' and repaired_df[col].isnull().any():
                    repaired_df[col].fillna(repaired_df[col].mode()[0], inplace=True)
                    
            return repaired_df, integrity_record
            
        except Exception as e:
            raise Exception(f"DRIL Agent execution failed: {str(e)}")
