"""
LOM Analysis Ledger Schema — Logging, Monitoring & Observability
Separate from GAL (CSV pipeline). Used for Root Cause Analysis of system data.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from datetime import datetime


def _coerce_to_list(v):
    if v is None:
        return []
    if isinstance(v, str):
        return [item.strip() for item in v.split(",") if item.strip()]
    return v


def _coerce_to_dict(v):
    if v is None:
        return {}
    if isinstance(v, str):
        return {"raw": v}
    return v


# --- Shared building blocks ---

class ParsedLogEntry(BaseModel):
    """A single normalized log line."""
    timestamp: Optional[str] = None
    level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARN, ERROR, FATAL")
    source: str = Field(default="", description="Service/host/filename that emitted this line")
    message: str = Field(default="")
    raw_line: str = Field(default="", description="Original unparsed line")
    line_number: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MetricDataPoint(BaseModel):
    """A single metric observation."""
    timestamp: Optional[str] = None
    metric_name: str = Field(default="")
    value: float = Field(default=0.0)
    unit: str = Field(default="")
    labels: Optional[Dict[str, str]] = Field(default_factory=dict)


class CodeArtifact(BaseModel):
    """A parsed code file or traceback."""
    filename: str = Field(default="")
    language: str = Field(default="unknown", description="python, javascript, yaml, etc.")
    content_preview: str = Field(default="", description="First ~200 lines or relevant excerpt")
    traceback: Optional[str] = Field(default=None, description="Extracted traceback/stack trace if present")
    error_type: Optional[str] = Field(default=None, description="Exception class name if detectable")
    error_message: Optional[str] = Field(default=None)
    functions_detected: Optional[List[str]] = Field(default_factory=list)


class LOMSourceFile(BaseModel):
    """Metadata about a single uploaded source file."""
    filename: str = Field(default="")
    file_type: str = Field(default="unknown", description="json, log, csv, python, javascript, yaml, text")
    size_bytes: int = Field(default=0)
    line_count: int = Field(default=0)
    time_range_start: Optional[str] = None
    time_range_end: Optional[str] = None
    parse_status: str = Field(default="pending", description="pending, success, partial, failed")
    parse_notes: str = Field(default="")
    entries_extracted: int = Field(default=0)


# --- Section 1: Source Inventory ---

class SourceInventory(BaseModel):
    """LOM Section 1 — What files were uploaded and their parsing status."""
    sources: List[LOMSourceFile] = Field(default_factory=list)
    total_files: int = Field(default=0)
    total_log_entries: int = Field(default=0)
    total_metric_points: int = Field(default=0)
    total_code_artifacts: int = Field(default=0)
    overall_time_range_start: Optional[str] = None
    overall_time_range_end: Optional[str] = None
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# --- Section 2: Log Profile ---

class LogLevelDistribution(BaseModel):
    level: str = Field(default="INFO")
    count: int = Field(default=0)
    percentage: float = Field(default=0.0)


class TopErrorMessage(BaseModel):
    message: str = Field(default="")
    count: int = Field(default=0)
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    source: str = Field(default="")


class LogProfile(BaseModel):
    """LOM Section 2 — Statistical profile of log data."""
    total_entries: int = Field(default=0)
    level_distribution: List[LogLevelDistribution] = Field(default_factory=list)
    error_rate_percent: float = Field(default=0.0)
    unique_sources: Optional[List[str]] = Field(default_factory=list)
    top_error_messages: List[TopErrorMessage] = Field(default_factory=list)
    error_burst_windows: Optional[List[str]] = Field(default_factory=list, description="Time windows with abnormal error rates")
    temporal_pattern: str = Field(default="", description="LLM-observed temporal pattern in the log data")
    overall_reasoning: str = Field(default="")
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("unique_sources", "error_burst_windows", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)


# --- Section 3: Metric Profile ---

class MetricSummary(BaseModel):
    metric_name: str = Field(default="")
    min_value: float = Field(default=0.0)
    max_value: float = Field(default=0.0)
    mean_value: float = Field(default=0.0)
    stddev: float = Field(default=0.0)
    anomaly_count: int = Field(default=0)
    unit: str = Field(default="")


class MetricProfile(BaseModel):
    """LOM Section 3 — Time-series metric summary."""
    total_data_points: int = Field(default=0)
    metrics: List[MetricSummary] = Field(default_factory=list)
    anomaly_windows: Optional[List[str]] = Field(default_factory=list)
    metric_log_correlations: Optional[List[str]] = Field(default_factory=list, description="Observed correlations between metric changes and log events")
    overall_reasoning: str = Field(default="")
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("anomaly_windows", "metric_log_correlations", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)


# --- Section 4: Code Context ---

class CodeContext(BaseModel):
    """LOM Section 4 — Parsed code artifacts and traceback analysis."""
    artifacts: List[CodeArtifact] = Field(default_factory=list)
    traceback_chains: Optional[List[str]] = Field(default_factory=list, description="Linked exception chains across files")
    error_relevant_snippets: Optional[List[str]] = Field(default_factory=list, description="Code lines implicated in errors")
    overall_reasoning: str = Field(default="")
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("traceback_chains", "error_relevant_snippets", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)


# --- Section 5: Timeline Reconstruction ---

class TimelineEvent(BaseModel):
    """A single event in the reconstructed timeline."""
    timestamp: Optional[str] = None
    event_type: str = Field(default="log", description="log, metric_anomaly, code_error, deployment, config_change")
    severity: str = Field(default="INFO", description="INFO, WARN, ERROR, CRITICAL")
    source: str = Field(default="")
    description: str = Field(default="")
    evidence_ref: str = Field(default="", description="Reference to Section 2/3/4 entry")


class TimelineReconstruction(BaseModel):
    """LOM Section 5 — Chronological event timeline merging all sources."""
    events: List[TimelineEvent] = Field(default_factory=list)
    total_events: int = Field(default=0)
    incident_window_start: Optional[str] = None
    incident_window_end: Optional[str] = None
    cascade_pattern: str = Field(default="", description="Detected failure cascade pattern")
    overall_reasoning: str = Field(default="")
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# --- Section 6: Anomaly Findings ---

class AnomalyEntry(BaseModel):
    """A single detected anomaly."""
    anomaly_type: str = Field(default="", description="error_spike, metric_drop, new_error_type, timeout_pattern, latency_spike")
    description: str = Field(default="")
    severity: str = Field(default="Medium", description="Low, Medium, High, Critical")
    time_window: Optional[str] = None
    affected_components: Optional[List[str]] = Field(default_factory=list)
    evidence: Optional[List[str]] = Field(default_factory=list, description="Supporting data references")
    confidence: str = Field(default="Moderate")

    @field_validator("affected_components", "evidence", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)


class AnomalyFindings(BaseModel):
    """LOM Section 6 — Detected anomalies across all data sources."""
    anomalies: List[AnomalyEntry] = Field(default_factory=list)
    total_anomalies: int = Field(default=0)
    critical_count: int = Field(default=0)
    overall_reasoning: str = Field(default="")
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# --- Section 7: RCA Hypotheses ---

class EvidenceChainLink(BaseModel):
    """A single link in an evidence chain."""
    source_type: str = Field(default="", description="log, metric, code, config")
    reference: str = Field(default="", description="Specific entry reference")
    observation: str = Field(default="")


class RCAHypothesis(BaseModel):
    """A single root cause hypothesis."""
    hypothesis: str = Field(default="", description="Proposed root cause in plain language")
    category: str = Field(default="", description="code_bug, config_error, resource_exhaustion, dependency_failure, deployment_issue, network_issue")
    evidence_chain: List[EvidenceChainLink] = Field(default_factory=list, description="Ordered evidence supporting this hypothesis")
    supporting_evidence: Optional[List[str]] = Field(default_factory=list)
    contradicting_evidence: Optional[List[str]] = Field(default_factory=list)
    affected_components: Optional[List[str]] = Field(default_factory=list)
    plausibility: str = Field(default="Moderate", description="High, Moderate, Low")
    reasoning: str = Field(default="")
    five_whys: Optional[List[str]] = Field(default_factory=list, description="5-Whys analysis chain")
    confidence_note: str = Field(default="")

    @field_validator("supporting_evidence", "contradicting_evidence", "affected_components", "five_whys", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)


class RCAHypotheses(BaseModel):
    """LOM Section 7 — Root cause hypotheses with evidence chains."""
    hypotheses: List[RCAHypothesis] = Field(default_factory=list)
    primary_suspect: str = Field(default="", description="The most likely root cause hypothesis")
    total_hypotheses: int = Field(default=0)
    overall_reasoning: str = Field(default="")
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# --- Section 8: RCA Report ---

class RemediationStep(BaseModel):
    """A single remediation suggestion."""
    action: str = Field(default="")
    priority: str = Field(default="Medium", description="Immediate, High, Medium, Low")
    estimated_impact: str = Field(default="")
    target_component: str = Field(default="")


class RCAReport(BaseModel):
    """LOM Section 8 — Final RCA narrative report."""
    executive_summary: str = Field(default="", description="2-3 sentence root cause summary")
    root_cause: str = Field(default="", description="Detailed root cause explanation")
    incident_timeline_narrative: str = Field(default="", description="Human-readable timeline story")
    affected_services: Optional[List[str]] = Field(default_factory=list)
    impact_assessment: str = Field(default="")
    remediation_steps: List[RemediationStep] = Field(default_factory=list)
    prevention_recommendations: Optional[List[str]] = Field(default_factory=list)
    confidence_level: str = Field(default="Moderate")
    citations: Optional[List[str]] = Field(default_factory=list, description="LOM_GAL section references")
    recorded_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("affected_services", "prevention_recommendations", "citations", mode="before")
    @classmethod
    def coerce_lists(cls, v):
        return _coerce_to_list(v)


# --- Master LOM Ledger ---

class LOMAnalysisLedger(BaseModel):
    """Master schema for the LOM analysis ledger (LOM_GAL.json)."""
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_type: str = Field(default="RCA", description="RCA, Anomaly Detection, Log Summarization")
    source_inventory: Optional[SourceInventory] = None
    log_profile: Optional[LogProfile] = None
    metric_profile: Optional[MetricProfile] = None
    code_context: Optional[CodeContext] = None
    timeline: Optional[TimelineReconstruction] = None
    anomaly_findings: Optional[AnomalyFindings] = None
    rca_hypotheses: Optional[RCAHypotheses] = None
    rca_report: Optional[RCAReport] = None
