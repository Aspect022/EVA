from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- GAL Section 1: Dataset Identity ---
class DatasetIdentity(BaseModel):
    domain: str = Field(description="The inferred real-world domain (e.g. Healthcare, E-commerce, Finance)")
    row_meaning: str = Field(description="What one row represents (e.g. one transaction, one patient visit)")
    time_behavior: str = Field(description="Static snapshot, time series, event log, or panel data")
    column_roles: Dict[str, str] = Field(description="Role of every column (e.g. identifier, feature, target candidate)")
    target_candidates: List[str] = Field(description="Possible target variables")
    health_observations: List[str] = Field(description="Data quality issues noted, not fixed yet")
    misinterpretation_risks: List[str] = Field(description="Columns that could be misused and why")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

# --- GAL Section 2: User Intent ---
class GeneratedQuestion(BaseModel):
    question: str = Field(description="The question text to present to the user")
    question_type: str = Field(description="One of: goal, stakeholder, priority, time")
    why_asked: str = Field(description="Brief reason why this question is relevant for this dataset")

class UserIntentRecord(BaseModel):
    analytical_goal: str = Field(description="Prediction, explanation, segmentation, anomaly detection, monitoring, or reporting")
    decision_supported: str = Field(description="The real-world decision the analysis is meant to support")
    stakeholder_type: str = Field(description="Student, business owner, researcher, analyst, manager")
    selected_target: Optional[str] = Field(default=None, description="The selected target variable if applicable")
    interpretability_priority: str = Field(description="How important is it that results be explainable vs. just accurate")
    constraints: List[str] = Field(description="Constraints like time, simplicity, reporting requirements")
    # New fields for guided conversation
    generated_questions: List[GeneratedQuestion] = Field(default_factory=list, description="Questions QBII generated for the user")
    user_responses: Dict[str, str] = Field(default_factory=dict, description="Map of question text -> user response")
    inferred_elements: List[str] = Field(default_factory=list, description="Fields that were inferred, not explicitly confirmed")
    user_confirmed: bool = Field(default=False, description="Whether the user confirmed the inferred intent")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

# --- GAL Section 3: Data Integrity Record ---
class ScriptExecution(BaseModel):
    """Tracks a single script execution by an agent."""
    script_path: str = Field(description="Path to the generated .py file")
    exit_code: int = Field(default=0, description="Process exit code")
    stdout: str = Field(default="", description="Captured stdout")
    stderr: str = Field(default="", description="Captured stderr")
    success: bool = Field(default=True, description="Whether the script ran successfully")

class ModificationRecord(BaseModel):
    problem: str = Field(description="The data quality problem found")
    impact: str = Field(description="Why it matters for this specific analysis")
    strategy_chosen: str = Field(description="The fix applied")
    alternatives_rejected: str = Field(default="", description="Other options considered but not used")
    effect: str = Field(default="", description="Rows affected, columns changed, etc.")
    confidence: str = Field(default="medium", description="Confidence level that the chosen strategy was correct")

class DataIntegrityRecord(BaseModel):
    modifications: List[ModificationRecord] = Field(default_factory=list)
    restricted_columns: Dict[str, str] = Field(default_factory=dict, description="Columns flagged as restricted and why")
    validation_result: str = Field(default="pending", description="Confirmation the repaired dataset represents original process")
    overall_reasoning: str = Field(default="", description="High-level explanation of WHY these cleaning decisions were made")
    script_execution: Optional[ScriptExecution] = Field(default=None, description="Details of the repair script that was executed")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

# --- GAL Section 4: Exploratory Findings ---
class ExploratoryFindings(BaseModel):
    distributions: Dict[str, Any] = Field(default_factory=dict, description="Distribution characteristics of key variables")
    correlations: List[Any] = Field(default_factory=list, description="Correlations between variables and their strength")
    anomalies: List[str] = Field(default_factory=list, description="Anomalies and unusual observations")
    target_associations: Dict[str, Any] = Field(default_factory=dict, description="Variables most associated with target")
    overall_reasoning: str = Field(default="", description="High-level interpretation of WHY these patterns matter")
    script_execution: Optional[ScriptExecution] = Field(default=None, description="Details of the exploration script that was executed")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

# --- Master GAL Model ---
class GlobalAnalysisLedger(BaseModel):
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    current_dataset_path: Optional[str] = Field(default=None, description="Path to the active CSV (snapshot -> repaired)")
    dataset_identity: Optional[DatasetIdentity] = None
    user_intent: Optional[UserIntentRecord] = None
    data_integrity: Optional[DataIntegrityRecord] = None
    exploratory_findings: Optional[ExploratoryFindings] = None
    # Future sections for Hypothesis, Feature Eng, ML models, etc.
