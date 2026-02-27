from pydantic import BaseModel
from typing import List, Optional, Dict,Any

class ModelDefinitionRecord(BaseModel):
    problem_type: Optional[str] = None
    target: Optional[str] = None
    features_used: Optional[List[str]] = []
    learning_view_features: Optional[List[str]] = None
    excluded_features: Optional[List[str]] = []
    split_strategy: Optional[str] = None
    train_size: Optional[int] = None
    validation_size: Optional[int] = None
    test_size: Optional[int] = None
    feasibility: Optional[str] = None

class CandidateModelRecord(BaseModel):
    candidates: Optional[List[str]] = None
    reasoning: Optional[Dict[str, str]] = None
    evaluation_metric: Optional[str] = None
    interpretability_level: Optional[str] = None

class ModelEvaluationRecord(BaseModel):
    results: Optional[Dict[str, Dict[str, float]]] = None
    overfitting_flags: Optional[Dict[str, bool]] = None
    selected_model: Optional[str] = None
    rejection_reasons: Optional[Dict[str, str]] = None
    stability_notes: Optional[Dict[str, str]] = None

class ModelValidationRecord(BaseModel):
    feature_importance: Optional[Dict[str, float]] = None
    hypothesis_alignment: Optional[str] = None
    leakage_detected: Optional[bool] = None
    sensitivity_score: Optional[float] = None
    confidence_profile: Optional[Dict[str, float]] = None
    validation_status: Optional[str] = None

class PredictionDeploymentRecord(BaseModel):
    deployment_status: Optional[str] = None
    model_path: Optional[str] = None
    prediction_schema: Optional[List[str]] = None
    monitoring_enabled: Optional[bool] = None
    drift_flag: Optional[bool] = None
    prediction_log_count: Optional[int] = None
    data_drift_score: Optional[float] = None
    confidence_drift_score: Optional[float] = None
    behavior_drift_score: Optional[float] = None
    retraining_recommended: Optional[bool] = None
    monitoring_notes: Optional[str] = None
    training_feature_means: Optional[Dict[str, float]] = None
    training_feature_stds: Optional[Dict[str, float]] = None
    baseline_avg_confidence: Optional[float] = None
    last_50_confidence_scores: Optional[List[float]] = []
    training_class_distribution: Optional[Dict[str, float]] = None
    recent_predictions: Optional[List[Any]] = []

class GovernanceRecord(BaseModel):
    model_version: Optional[str] = None
    model_hash: Optional[str] = None
    gal_snapshot_hash: Optional[str] = None
    training_timestamp: Optional[str] = None
    deployment_timestamp: Optional[str] = None
    reproducibility_verified: Optional[bool] = None
    audit_log_path: Optional[str] = None
    sla_tier: Optional[str] = None
    compliance_tags: Optional[List[str]] = None
