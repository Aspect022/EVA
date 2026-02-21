from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import UserIntentRecord, DatasetIdentity

class QBIIAgent:
    """
    Question Builder & Intent Inference Agent.
    Infers the analytical goal based on the dataset's real-world identity if the user hasn't explicitly supplied one.
    """
    
    @staticmethod
    def execute(dataset_identity: DatasetIdentity) -> UserIntentRecord:
        system_prompt = """You are EVA's Question Builder & Intent Inference (QBII) module.
        Your job is to look at the dataset identity inferred by the profiling layer and deduce the most likely analytical goal for the user.
        What is the primary decision being supported? Are they solving for prediction, explanation, or segmentation?
        You must write your intent hypothesis into the Global Analysis Ledger (GAL)."""
        
        try:
            user_prompt = f"Infer analytical intent from this Dataset Identity:\n{dataset_identity.model_dump_json(indent=2)}"
            
            return invoke_agent(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                pydantic_schema=UserIntentRecord
            )
            
        except Exception as e:
            raise Exception(f"QBII Agent execution failed: {str(e)}")
