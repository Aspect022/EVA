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
class UserIntentRecord(BaseModel):
    analytical_goal: str = Field(description="Prediction, explanation, segmentation, anomaly detection, monitoring, or reporting")
    decision_supported: str = Field(description="The real-world decision the analysis is meant to support")
    stakeholder_type: str = Field(description="Student, business owner, researcher, analyst, manager")
    selected_target: Optional[str] = Field(description="The selected target variable if applicable")
    interpretability_priority: str = Field(description="How important is it that results be explainable vs. just accurate")
    constraints: List[str] = Field(description="Constraints like time, simplicity, reporting requirements")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

# --- GAL Section 3: Data Integrity Record ---
class ModificationRecord(BaseModel):
    problem: str
    impact: str = Field(description="Why it matters for this specific analysis")
    strategy_chosen: str
    alternatives_rejected: str
    effect: str = Field(description="Rows affected, columns changed, etc.")
    confidence: str = Field(description="Confidence level that the chosen strategy was correct")

class DataIntegrityRecord(BaseModel):
    modifications: List[ModificationRecord]
    restricted_columns: Dict[str, str] = Field(description="Columns flagged as restricted and why")
    validation_result: str = Field(description="Confirmation the repaired dataset represents original process")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

# --- GAL Section 4: Exploratory Findings ---
class ExploratoryFindings(BaseModel):
    distributions: Dict[str, Dict[str, Any]] = Field(description="Distribution characteristics of key variables")
    correlations: List[Dict[str, Any]] = Field(description="Correlations between variables and their strength")
    anomalies: List[str] = Field(description="Anomalies and unusual observations")
    target_associations: Dict[str, str] = Field(description="Variables most associated with target")
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

# --- Master GAL Model ---
class GlobalAnalysisLedger(BaseModel):
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    dataset_identity: Optional[DatasetIdentity] = None
    user_intent: Optional[UserIntentRecord] = None
    data_integrity: Optional[DataIntegrityRecord] = None
    exploratory_findings: Optional[ExploratoryFindings] = None
    # Future sections for Hypothesis, Future Eng, ML models, etc.
