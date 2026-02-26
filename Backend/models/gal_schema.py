from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime


def _coerce_to_list(v):
    """Accept a string and split into list, or pass through lists."""
    if v is None:
        return []
    if isinstance(v, str):
        return [item.strip() for item in v.split(",") if item.strip()]
    return v


def _coerce_to_dict(v):
    """Accept a string and return as-is in a wrapper, or pass through dicts."""
    if v is None:
        return {}
    if isinstance(v, str):
        return {"raw": v}
    return v


# --- GAL Section 1: Dataset Identity ---
class DatasetIdentity(BaseModel):
    # Core fields (always expected from both lite and full rules)
    domain: str = Field(default="UNKNOWN")
    dataset_type: str = Field(default="UNKNOWN")
    has_target_column: bool = False
    inferred_target_column: Optional[str] = None
    label_type: str = Field(default="UNKNOWN")
    has_temporal_column: bool = False
    temporal_column_name: Optional[str] = None
    has_group_column: bool = False
    group_column_name: Optional[str] = None
    has_pii_detected: bool = False
    pii_column_candidates: Optional[List[str] | str] = Field(default_factory=list)
    protected_attribute_flag: bool = False
    n_rows: Optional[int | str] = None
    n_features: Optional[int | str] = None
    domain_risk_flag: str = Field(default="LOW")
    regulatory_exposure_flag: bool = False

    # Legacy V1 fields (optional — produced by full rules only)
    row_meaning: Optional[str] = None
    time_behavior: Optional[str] = None
    column_roles: Optional[Dict[str, str] | str] = None
    target_candidates: Optional[List[str] | str] = None
    health_observations: Optional[List[str] | str] = None
    misinterpretation_risks: Optional[List[str] | str] = None
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("pii_column_candidates", "target_candidates", "health_observations", "misinterpretation_risks", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)

    @field_validator("column_roles", mode="before")
    @classmethod
    def coerce_dict(cls, v):
        return _coerce_to_dict(v)

    @field_validator("n_rows", "n_features", mode="before")
    @classmethod
    def coerce_int(cls, v):
        if v is None or v == "UNKNOWN":
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None


# --- GAL Section 2: User Intent ---
class GeneratedQuestion(BaseModel):
    question: str = Field(description="The question text to present to the user")
    question_type: str = Field(description="One of: goal, stakeholder, priority, time")
    why_asked: str = Field(description="Brief reason why this question is relevant for this dataset")


class CostMatrix(BaseModel):
    FP_cost_relative: float | str = 1.0
    FN_cost_relative: float | str = 1.0
    cost_asymmetry: str = "symmetric"


class UserIntentRecord(BaseModel):
    # V2.0 Fields from IntentInferenceRules.md
    session_id: Optional[str] = None
    dataset_identity_ref: Optional[str] = None
    primary_objective: str = Field(default="PREDICT")
    deployment_mode: str = Field(default="HUMAN_REVIEWED")
    decision_impact: str = Field(default="ANALYTICAL")
    risk_tier: str = Field(default="TIER_3")
    interpretability_tier: int | str = Field(default=3)
    regulatory_mode: str = Field(default="STANDARD")
    regulatory_frameworks: Optional[List[str] | str] = Field(default_factory=lambda: ["NONE"])
    domain_override: Optional[str] = None
    cost_matrix: Optional[CostMatrix | Dict[str, Any] | str] = None
    error_cost_direction: str = Field(default="UNKNOWN")
    fairness_sensitivity: str = Field(default="LOW")
    fairness_reporting_required: bool = False
    time_awareness: str = Field(default="NONE")
    temporal_split_required: bool = False
    explanation_requirement: str = Field(default="NONE")
    gdpr_art22_flag: bool = False
    inference_confidence: str = Field(default="LOW")
    escalation_required: bool = False
    escalation_reasons: Optional[List[str] | str] = Field(default_factory=list)
    conservative_overrides_applied: Optional[List[str] | str] = Field(default_factory=list)
    timestamp: Optional[datetime | str] = Field(default_factory=datetime.utcnow)

    # Legacy V1 / UI Fields (Optional to avoid validation errors)
    analytical_goal: Optional[str] = None
    decision_supported: Optional[str] = None
    stakeholder_type: Optional[str] = None
    selected_target: Optional[str] = None
    interpretability_priority: Optional[str] = None
    constraints: Optional[List[str] | str] = None

    # Internal state tracking
    generated_questions: List[GeneratedQuestion] = Field(default_factory=list)
    user_responses: Dict[str, str] = Field(default_factory=dict)
    inferred_elements: Optional[List[str] | str] = Field(default_factory=list)
    user_confirmed: bool = Field(default=False)
    recorded_at: Optional[datetime | str] = Field(default_factory=datetime.utcnow)

    @field_validator("regulatory_frameworks", "escalation_reasons", "conservative_overrides_applied", "constraints", "inferred_elements", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)


# --- GAL Section 3: Data Integrity Record ---
class ScriptExecution(BaseModel):
    """Tracks a single script execution by an agent."""
    script_path: str = Field(default="")
    exit_code: int = Field(default=0)
    stdout: str = Field(default="")
    stderr: str = Field(default="")
    success: bool = Field(default=True)


class ModificationRecord(BaseModel):
    problem: str = Field(default="")
    impact: str = Field(default="")
    strategy_chosen: str = Field(default="")
    alternatives_rejected: str = Field(default="")
    effect: str = Field(default="")
    confidence: str | float = Field(default="medium")


class DataIntegrityRecord(BaseModel):
    modifications: Optional[List[ModificationRecord] | str] = Field(default_factory=list)
    restricted_columns: Optional[Dict[str, str] | str] = Field(default_factory=dict)
    validation_result: str = Field(default="pending")
    overall_reasoning: str = Field(default="")
    script_execution: Optional[ScriptExecution] = None
    recorded_at: Optional[datetime | str] = Field(default_factory=datetime.utcnow)

    @field_validator("restricted_columns", mode="before")
    @classmethod
    def coerce_dict(cls, v):
        return _coerce_to_dict(v)


# --- GAL Section 4: Exploratory Findings ---
class ExploratoryFindings(BaseModel):
    distributions: Optional[Dict[str, Any] | str] = Field(default_factory=dict)
    correlations: Optional[List[Any] | str] = Field(default_factory=list)
    anomalies: Optional[List[str] | str] = Field(default_factory=list)
    target_associations: Optional[Dict[str, Any] | str] = Field(default_factory=dict)
    overall_reasoning: str = Field(default="")
    script_execution: Optional[ScriptExecution] = None
    recorded_at: Optional[datetime | str] = Field(default_factory=datetime.utcnow)

    @field_validator("anomalies", "correlations", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)

    @field_validator("distributions", "target_associations", mode="before")
    @classmethod
    def coerce_dicts(cls, v):
        return _coerce_to_dict(v)


# --- Master GAL Model ---
class GlobalAnalysisLedger(BaseModel):
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    current_dataset_path: Optional[str] = None
    dataset_identity: Optional[DatasetIdentity] = None
    user_intent: Optional[UserIntentRecord] = None
    data_integrity: Optional[DataIntegrityRecord] = None
    exploratory_findings: Optional[ExploratoryFindings] = None
    # Future sections for Hypothesis, Feature Eng, ML models, etc.
