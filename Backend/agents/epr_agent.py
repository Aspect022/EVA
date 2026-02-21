import pandas as pd
from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import ExploratoryFindings, DatasetIdentity

class EPRAgent:
    """
    Exploration & Pattern Recognition.
    Calculates basic statistical attributes to inform the analyst (or downstream models) of shape, distributions, and outliers.
    """

    @staticmethod
    def _interpret_findings(statistical_summary: str, identity: DatasetIdentity) -> ExploratoryFindings:
        system_prompt = """You are EVA's Exploration & Pattern Recognition (EPR) module.
        Your job is to read statistical metrics generated from a dataset and interpret their real-world meaning.
        Identify the primary anomalies and variable relationships based on the domain context provided.
        Write your findings directly to the Global Analysis Ledger (GAL)."""
        
        user_prompt = f"""
        Identity Context:\n{identity.model_dump_json(indent=2)}
        Statistical Patterns:\n{statistical_summary}
        """
        
        return invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=ExploratoryFindings
        )

    @staticmethod
    def execute(dataframe: pd.DataFrame, identity: DatasetIdentity) -> ExploratoryFindings:
        try:
            # Generate pure statistical summary
            desc = dataframe.describe(include='all').to_dict()
            
            # Very basic correlation map for numeric columns
            numeric_df = dataframe.select_dtypes(include=['float64', 'int64'])
            corr = numeric_df.corr().to_dict() if not numeric_df.empty else {}
            
            stats = f"Distributions: {desc}\nCorrelations: {corr}"
            
            # Obtain the semantic interpretation of the raw metrics
            findings = EPRAgent._interpret_findings(stats, identity)
            
            # Bind the raw computed data directly to the structural JSON prior to return
            findings.distributions = desc
            findings.correlations = [{"matrix": corr}] # Simplified structure mapping for phase 1
            
            return findings
            
        except Exception as e:
            raise Exception(f"EPR Agent execution failed: {str(e)}")
