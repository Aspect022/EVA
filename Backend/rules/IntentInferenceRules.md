# IntentInferenceRules.md
## Enterprise Intent Inference Engine — Backend Governance Specification
**Version:** 2.0
**Reads:** RawAnswerRecord (from QuestionBuilderRules)
**Reads:** DatasetIdentity (from GAL, produced by DomainAnalysisRules)
**Produces:** UserIntentRecord → consumed by DRIL, EPR, DataScienceRules engine
**Constraint:** All output fields must map to exact enum values used in DataScienceRules.md

---

## Input Contract

```
RawAnswerRecord:
  session_id:               UUID
  dataset_identity_ref:     DatasetIdentity.id
  questions_issued:         [Q_IDs]
  answers:                  {Q_ID: selected_option}
  ambiguity_flags:          {flag_name: Boolean}
  conservative_fallbacks_applied: [field_names]

DatasetIdentity:
  domain:                   BANKING | HEALTHCARE | INSURANCE | GENERAL | UNKNOWN
  dataset_type:             TABULAR | TIME_SERIES | PANEL | NLP | CV | GRAPH | UNKNOWN
  has_target_column:        Boolean
  has_temporal_column:      Boolean
  n_rows:                   Integer or UNKNOWN
  label_type:               BINARY | MULTICLASS | REGRESSION | NONE | UNKNOWN
  domain_risk_flag:         LOW | MODERATE | HIGH | CRITICAL
  regulatory_exposure_flag: Boolean
  protected_attribute_flag: Boolean
```

---

## Output Contract

IntentInferenceRules produces a fully populated UserIntentRecord:

```
UserIntentRecord:
  session_id:               UUID
  dataset_identity_ref:     DatasetIdentity.id
  primary_objective:        PREDICT | EXPLAIN | SEGMENT | ANOMALY_DETECT | FORECAST
  deployment_mode:          AUTOMATED | HUMAN_REVIEWED | HYBRID
  decision_impact:          FINANCIAL_INDIVIDUAL | HEALTH_SAFETY | LEGAL_STATUS | OPERATIONAL | ANALYTICAL
  risk_tier:                TIER_1 | TIER_2 | TIER_3
  interpretability_tier:    1 | 2 | 3
  regulatory_mode:          STANDARD | REGULATED | GDPR_STRICT
  regulatory_frameworks:    [SR_11_7, GDPR, SECTOR_CLINICAL, MULTI, INTERNAL, NONE]
  domain_override:          BANKING | HEALTHCARE | INSURANCE | GENERAL | NULL
  cost_matrix:              {FP_cost_relative, FN_cost_relative, cost_asymmetry}
  error_cost_direction:     FN_DOMINANT | FP_DOMINANT | SYMMETRIC | UNKNOWN
  fairness_sensitivity:     HIGH | MODERATE | LOW
  fairness_reporting_required: Boolean
  time_awareness:           FORECAST | POINT_IN_TIME_STRICT | TREND_ANALYSIS | NONE
  temporal_split_required:  Boolean
  explanation_requirement:  INDIVIDUAL_FACING | AUDIT_FACING | BOTH | NONE
  gdpr_art22_flag:          Boolean
  inference_confidence:     HIGH | MEDIUM | LOW
  escalation_required:      Boolean
  escalation_reasons:       [list of strings]
  conservative_overrides_applied: [list of field names where conservative default used]
  timestamp:                ISO timestamp
```

---

## Inference Rules

### BLOCK 1 — Primary Objective Inference

```python
answer_Q1 = RawAnswerRecord.answers.get("Q1")

IF answer_Q1 == "a":
    primary_objective = PREDICT
ELIF answer_Q1 == "b":
    primary_objective = EXPLAIN
ELIF answer_Q1 == "c":
    primary_objective = SEGMENT
ELIF answer_Q1 == "d":
    primary_objective = ANOMALY_DETECT
ELIF answer_Q1 == "e":
    primary_objective = FORECAST
ELIF answer_Q1 IS NULL:
    primary_objective = PREDICT  # conservative default
    conservative_overrides_applied.append("primary_objective")
    inference_confidence = LOW

# Dataset type cross-check
IF primary_objective == FORECAST AND DatasetIdentity.dataset_type NOT IN [TIME_SERIES, PANEL]:
    SET warning = "User selected FORECAST but dataset_type is not TIME_SERIES or PANEL."
    SET inference_confidence = MEDIUM
    PASS warning to UserIntentRecord metadata

IF primary_objective == PREDICT AND DatasetIdentity.has_target_column == False:
    SET escalation_required = True
    escalation_reasons.append("PREDICT objective selected but no target column detected in dataset.")
```

---

### BLOCK 2 — Deployment Mode Inference

```python
answer_Q2 = RawAnswerRecord.answers.get("Q2")

IF answer_Q2 == "a":
    deployment_mode = AUTOMATED
ELIF answer_Q2 == "b":
    deployment_mode = HUMAN_REVIEWED
ELIF answer_Q2 == "c":
    deployment_mode = HYBRID
ELIF answer_Q2 == "d":
    deployment_mode = HUMAN_REVIEWED
    decision_impact_floor = ANALYTICAL
ELIF answer_Q2 IS NULL AND primary_objective IN [EXPLAIN, SEGMENT]:
    deployment_mode = HUMAN_REVIEWED  # default for non-predictive objectives
ELIF answer_Q2 IS NULL:
    deployment_mode = HUMAN_REVIEWED  # conservative default
    conservative_overrides_applied.append("deployment_mode")
```

---

### BLOCK 3 — Decision Impact and Risk Tier Inference

```python
answer_Q3 = RawAnswerRecord.answers.get("Q3")

# Map answer to impact domain
impact_map = {
    "a": "FINANCIAL_INDIVIDUAL",
    "b": "HEALTH_SAFETY",
    "c": "LEGAL_STATUS",
    "d": "OPERATIONAL",
    "e": "ANALYTICAL"
}

IF answer_Q3 IS NOT NULL:
    decision_impact = impact_map[answer_Q3]
ELIF DatasetIdentity.domain == BANKING:
    decision_impact = FINANCIAL_INDIVIDUAL
    conservative_overrides_applied.append("decision_impact")
ELIF DatasetIdentity.domain == HEALTHCARE:
    decision_impact = HEALTH_SAFETY
    conservative_overrides_applied.append("decision_impact")
ELIF DatasetIdentity.domain == INSURANCE:
    decision_impact = FINANCIAL_INDIVIDUAL
    conservative_overrides_applied.append("decision_impact")
ELSE:
    decision_impact = OPERATIONAL
    conservative_overrides_applied.append("decision_impact")

# Risk tier derivation
IF decision_impact IN [FINANCIAL_INDIVIDUAL, HEALTH_SAFETY, LEGAL_STATUS]:
    risk_tier_floor = TIER_1
ELIF decision_impact == OPERATIONAL:
    risk_tier_floor = TIER_2
ELSE:
    risk_tier_floor = TIER_3

# Deployment mode elevation
IF deployment_mode == AUTOMATED AND risk_tier_floor == TIER_2:
    risk_tier_floor = TIER_1  # automated decisions on operational impact elevate to Tier 1
    conservative_overrides_applied.append("risk_tier_automated_elevation")

IF deployment_mode == HUMAN_REVIEWED AND risk_tier_floor == TIER_1:
    risk_tier = TIER_1  # human review does not lower tier when impact is individual-facing

# DatasetIdentity domain_risk_flag cross-check
IF DatasetIdentity.domain_risk_flag == CRITICAL AND risk_tier_floor != TIER_1:
    risk_tier_floor = TIER_1
    conservative_overrides_applied.append("risk_tier_domain_critical_override")

risk_tier = risk_tier_floor
```

---

### BLOCK 4 — Interpretability Tier Inference

```python
answer_Q4 = RawAnswerRecord.answers.get("Q4")

IF answer_Q4 == "a":
    explanation_requirement = INDIVIDUAL_FACING
    interpretability_tier = 1
    gdpr_art22_flag = True
ELIF answer_Q4 == "b":
    explanation_requirement = AUDIT_FACING
    interpretability_tier = 1
    gdpr_art22_flag = False
ELIF answer_Q4 == "c":
    explanation_requirement = BOTH
    interpretability_tier = 1
    gdpr_art22_flag = True
ELIF answer_Q4 == "d":
    explanation_requirement = NONE
    interpretability_tier_from_q4 = 2
ELIF answer_Q4 IS NULL:
    # Q4 not issued: derive from risk_tier
    IF risk_tier == TIER_1:
        interpretability_tier_from_q4 = 1
        explanation_requirement = AUDIT_FACING  # conservative default
    ELIF risk_tier == TIER_2:
        interpretability_tier_from_q4 = 2
        explanation_requirement = NONE
    ELSE:
        interpretability_tier_from_q4 = 3
        explanation_requirement = NONE
    conservative_overrides_applied.append("interpretability_tier")

# Enforce floor based on risk_tier and decision_impact
IF risk_tier == TIER_1 AND answer_Q4 IS NOT NULL:
    interpretability_tier = min(1, interpretability_tier_from_q4)
    # interpretability_tier can only be 1 for Tier 1 risk
ELIF risk_tier == TIER_2:
    interpretability_tier = min(2, interpretability_tier_from_q4)
ELSE:
    interpretability_tier = interpretability_tier_from_q4

# GDPR Art. 22 override
IF gdpr_art22_flag == True:
    interpretability_tier = 1  # mandatory regardless of other inputs

# Dataset type constraint cross-check
IF DatasetIdentity.dataset_type == NLP AND interpretability_tier == 1:
    SET escalation_required = True
    escalation_reasons.append("NLP dataset with interpretability_tier=1 is architecturally incompatible. Use case scope must be reviewed.")

IF DatasetIdentity.dataset_type == CV AND interpretability_tier IN [1, 2]:
    SET escalation_required = True
    escalation_reasons.append("Computer vision dataset with interpretability_tier<=2 is architecturally incompatible.")
```

---

### BLOCK 5 — Regulatory Mode Inference

```python
answer_Q7 = RawAnswerRecord.answers.get("Q7")

IF answer_Q7 IS NOT NULL:
    selected_options = answer_Q7  # multi-select list
    
    IF "b" IN selected_options OR "d" IN selected_options:
        regulatory_mode = GDPR_STRICT
        # GDPR_STRICT supersedes REGULATED
    ELIF "a" IN selected_options OR "c" IN selected_options:
        regulatory_mode = REGULATED
    ELIF "e" IN selected_options:
        regulatory_mode = STANDARD
    ELIF "f" IN selected_options:
        regulatory_mode = STANDARD
    ELSE:
        regulatory_mode = STANDARD

    # Framework list construction
    framework_map = {
        "a": SR_11_7,
        "b": GDPR,
        "c": SECTOR_CLINICAL,
        "d": MULTI,
        "e": INTERNAL,
        "f": NONE
    }
    regulatory_frameworks = [framework_map[o] for o in selected_options]

ELSE:
    # Q7 not issued or not answered: derive from domain and risk_tier
    IF DatasetIdentity.domain == BANKING:
        regulatory_mode = REGULATED
        regulatory_frameworks = [SR_11_7]
        conservative_overrides_applied.append("regulatory_mode_banking_default")
    
    ELIF DatasetIdentity.domain == HEALTHCARE:
        regulatory_mode = REGULATED
        regulatory_frameworks = [SECTOR_CLINICAL]
        conservative_overrides_applied.append("regulatory_mode_healthcare_default")
    
    ELIF DatasetIdentity.domain == INSURANCE:
        regulatory_mode = REGULATED
        regulatory_frameworks = [SECTOR_CLINICAL]
        conservative_overrides_applied.append("regulatory_mode_insurance_default")
    
    ELIF risk_tier == TIER_1:
        regulatory_mode = REGULATED
        regulatory_frameworks = [INTERNAL]
        conservative_overrides_applied.append("regulatory_mode_tier1_default")
    
    ELSE:
        regulatory_mode = STANDARD
        regulatory_frameworks = [NONE]

# Conservative escalation: underspecified regulatory exposure
IF deployment_mode == AUTOMATED AND risk_tier == TIER_1 AND regulatory_mode == STANDARD:
    regulatory_mode = REGULATED
    conservative_overrides_applied.append("regulatory_mode_automated_tier1_escalation")
    LOG warning: "Automated Tier 1 deployment with STANDARD regulatory mode is not permitted. Elevated to REGULATED."

# GDPR Art. 22 trigger elevation
IF gdpr_art22_flag == True AND regulatory_mode == STANDARD:
    regulatory_mode = GDPR_STRICT
    conservative_overrides_applied.append("regulatory_mode_gdpr_art22_elevation")
```

---

### BLOCK 6 — Cost Matrix Inference

```python
answer_Q5 = RawAnswerRecord.answers.get("Q5")

IF answer_Q5 == "a":
    error_cost_direction = FN_DOMINANT
    cost_asymmetry = HIGH
    cost_matrix = {
        FP_cost_relative: 1.0,
        FN_cost_relative: 5.0,
        cost_asymmetry: HIGH
    }

ELIF answer_Q5 == "b":
    error_cost_direction = FP_DOMINANT
    cost_asymmetry = HIGH
    cost_matrix = {
        FP_cost_relative: 5.0,
        FN_cost_relative: 1.0,
        cost_asymmetry: HIGH
    }

ELIF answer_Q5 == "c":
    error_cost_direction = SYMMETRIC
    cost_asymmetry = LOW
    cost_matrix = {
        FP_cost_relative: 1.0,
        FN_cost_relative: 1.0,
        cost_asymmetry: LOW
    }

ELIF answer_Q5 == "d":
    error_cost_direction = UNKNOWN
    cost_asymmetry = UNKNOWN
    # Conservative domain-based fallback
    IF DatasetIdentity.domain == HEALTHCARE AND decision_impact == HEALTH_SAFETY:
        error_cost_direction = FN_DOMINANT
        cost_matrix = {FP_cost_relative: 1.0, FN_cost_relative: 10.0, cost_asymmetry: HIGH}
        conservative_overrides_applied.append("cost_matrix_healthcare_fn_dominant_default")
    
    ELIF DatasetIdentity.domain == BANKING AND decision_impact == FINANCIAL_INDIVIDUAL:
        error_cost_direction = FN_DOMINANT
        cost_matrix = {FP_cost_relative: 1.0, FN_cost_relative: 5.0, cost_asymmetry: HIGH}
        conservative_overrides_applied.append("cost_matrix_banking_fn_dominant_default")
    
    ELSE:
        error_cost_direction = SYMMETRIC
        cost_matrix = {FP_cost_relative: 1.0, FN_cost_relative: 1.0, cost_asymmetry: LOW}
        conservative_overrides_applied.append("cost_matrix_symmetric_default")
    
    SET ambiguity_flag["cost_matrix_unknown"] = True

ELIF answer_Q5 IS NULL:
    # Q5 not issued: no cost-sensitive learning requirement
    error_cost_direction = SYMMETRIC
    cost_matrix = {FP_cost_relative: 1.0, FN_cost_relative: 1.0, cost_asymmetry: LOW}
```

---

### BLOCK 7 — Fairness Sensitivity Inference

```python
answer_Q6 = RawAnswerRecord.answers.get("Q6")

IF answer_Q6 == "a":
    fairness_sensitivity = HIGH
    fairness_reporting_required = True
ELIF answer_Q6 == "b":
    fairness_sensitivity = MODERATE
    fairness_reporting_required = False
ELIF answer_Q6 == "c":
    fairness_sensitivity = MODERATE
    fairness_reporting_required = False
ELIF answer_Q6 == "d":
    fairness_sensitivity = LOW
    fairness_reporting_required = False
ELIF answer_Q6 IS NULL:
    # Q6 not issued or not answered: derive from dataset signals
    IF DatasetIdentity.protected_attribute_flag == True:
        fairness_sensitivity = MODERATE
        conservative_overrides_applied.append("fairness_sensitivity_pii_default")
    ELIF DatasetIdentity.domain IN [BANKING, HEALTHCARE, INSURANCE]:
        fairness_sensitivity = MODERATE
        conservative_overrides_applied.append("fairness_sensitivity_domain_default")
    ELSE:
        fairness_sensitivity = LOW
    fairness_reporting_required = False

# Regulatory mode elevation from fairness
IF fairness_sensitivity == HIGH AND regulatory_mode == STANDARD:
    regulatory_mode = REGULATED
    conservative_overrides_applied.append("regulatory_mode_fairness_high_elevation")
```

---

### BLOCK 8 — Time Awareness Inference

```python
answer_Q8 = RawAnswerRecord.answers.get("Q8")

IF answer_Q8 == "a":
    time_awareness = FORECAST
    temporal_split_required = True
    gap_injection_required = True
ELIF answer_Q8 == "b":
    time_awareness = POINT_IN_TIME_STRICT
    temporal_split_required = True
    gap_injection_required = True
ELIF answer_Q8 == "c":
    time_awareness = TREND_ANALYSIS
    temporal_split_required = True
    gap_injection_required = False
ELIF answer_Q8 == "d":
    time_awareness = NONE
    temporal_split_required = False
    gap_injection_required = False
ELIF answer_Q8 IS NULL:
    # Derive from DatasetIdentity
    IF DatasetIdentity.dataset_type IN [TIME_SERIES, PANEL] OR DatasetIdentity.has_temporal_column == True:
        time_awareness = POINT_IN_TIME_STRICT  # conservative default for temporal datasets
        temporal_split_required = True
        gap_injection_required = True
        conservative_overrides_applied.append("time_awareness_temporal_dataset_default")
    ELSE:
        time_awareness = NONE
        temporal_split_required = False
        gap_injection_required = False
```

---

### BLOCK 9 — Domain Override Detection

```python
# Check if user's answers imply a domain different from DatasetIdentity.domain

user_implied_domain = NULL

IF decision_impact == FINANCIAL_INDIVIDUAL AND DatasetIdentity.domain NOT IN [BANKING, INSURANCE]:
    user_implied_domain = BANKING
ELIF decision_impact == HEALTH_SAFETY AND DatasetIdentity.domain != HEALTHCARE:
    user_implied_domain = HEALTHCARE

IF user_implied_domain IS NOT NULL AND DatasetIdentity.domain != UNKNOWN:
    IF user_implied_domain != DatasetIdentity.domain:
        SET domain_conflict_flag = True
        LOG: f"User answers imply domain={user_implied_domain} but DatasetIdentity.domain={DatasetIdentity.domain}."
        domain_override = user_implied_domain
        # User intent takes precedence over automated domain detection for governance purposes
    ELSE:
        domain_override = NULL
ELIF user_implied_domain IS NOT NULL:
    domain_override = user_implied_domain
ELSE:
    domain_override = NULL
```

---

### BLOCK 10 — Inference Confidence Scoring

```python
confidence_deductions = 0

IF "cost_matrix_unknown" IN ambiguity_flags AND ambiguity_flags["cost_matrix_unknown"] == True:
    confidence_deductions += 1

IF conservative_overrides_applied.count > 3:
    confidence_deductions += 1

IF escalation_required == True:
    confidence_deductions += 2

IF domain_conflict_flag == True:
    confidence_deductions += 1

IF DatasetIdentity.domain == UNKNOWN:
    confidence_deductions += 1

IF confidence_deductions == 0:
    inference_confidence = HIGH
ELIF confidence_deductions <= 2:
    inference_confidence = MEDIUM
ELSE:
    inference_confidence = LOW
```

---

## Escalation Rules

```python
# Hard escalation conditions: these block downstream processing until resolved

ESCALATION_CONDITIONS = [
    {
        "condition": primary_objective == PREDICT AND DatasetIdentity.has_target_column == False,
        "reason": "PREDICT_NO_TARGET_COLUMN",
        "action": "HALT_PIPELINE_REQUIRE_HUMAN_RESOLUTION"
    },
    {
        "condition": DatasetIdentity.dataset_type == NLP AND interpretability_tier == 1,
        "reason": "NLP_INTERPRETABILITY_CONFLICT",
        "action": "HALT_PIPELINE_REQUIRE_USE_CASE_SCOPE_REVISION"
    },
    {
        "condition": DatasetIdentity.dataset_type == CV AND interpretability_tier <= 2,
        "reason": "CV_INTERPRETABILITY_CONFLICT",
        "action": "HALT_PIPELINE_REQUIRE_USE_CASE_SCOPE_REVISION"
    },
    {
        "condition": deployment_mode == AUTOMATED AND risk_tier == TIER_1 AND explanation_requirement == NONE AND gdpr_art22_flag == True,
        "reason": "GDPR_ART22_EXPLANATION_REQUIRED_BUT_NOT_CONFIGURED",
        "action": "HALT_PIPELINE_REQUIRE_COMPLIANCE_REVIEW"
    },
    {
        "condition": inference_confidence == LOW AND risk_tier == TIER_1,
        "reason": "LOW_CONFIDENCE_TIER1_INFERENCE",
        "action": "ESCALATE_TO_MODEL_RISK_BEFORE_PROCEEDING"
    }
]

FOR each condition in ESCALATION_CONDITIONS:
    IF condition.condition == True:
        SET escalation_required = True
        escalation_reasons.append(condition.reason)
        SET escalation_action = condition.action
```

---

## Validation Rules

Run after all inference blocks complete, before writing UserIntentRecord.

```python
# Rule V1: Automated + Tier 1 must have interpretability_tier = 1
IF deployment_mode == AUTOMATED AND risk_tier == TIER_1:
    IF interpretability_tier != 1:
        interpretability_tier = 1
        conservative_overrides_applied.append("interpretability_enforced_automated_tier1")

# Rule V2: GDPR_STRICT requires gdpr_art22_flag or individual-facing explanation
IF regulatory_mode == GDPR_STRICT:
    IF gdpr_art22_flag == False AND explanation_requirement == NONE AND decision_impact IN [FINANCIAL_INDIVIDUAL, HEALTH_SAFETY, LEGAL_STATUS]:
        gdpr_art22_flag = True
        explanation_requirement = INDIVIDUAL_FACING
        conservative_overrides_applied.append("gdpr_art22_flag_enforced_strict_mode")

# Rule V3: FORECAST requires temporal_split_required = True
IF primary_objective == FORECAST:
    IF temporal_split_required == False:
        temporal_split_required = True
        conservative_overrides_applied.append("temporal_split_enforced_forecast_objective")

# Rule V4: SEGMENT and EXPLAIN cannot be AUTOMATED
IF primary_objective IN [SEGMENT, EXPLAIN] AND deployment_mode == AUTOMATED:
    deployment_mode = HUMAN_REVIEWED
    conservative_overrides_applied.append("deployment_mode_corrected_non_predictive_objective")

# Rule V5: ANOMALY_DETECT should default to HYBRID if deployment_mode is AUTOMATED
IF primary_objective == ANOMALY_DETECT AND deployment_mode == AUTOMATED:
    deployment_mode = HYBRID
    conservative_overrides_applied.append("deployment_mode_anomaly_detect_hybrid_default")

# Rule V6: Cost matrix must exist for Tier 1 automated deployments
IF risk_tier == TIER_1 AND deployment_mode == AUTOMATED:
    IF cost_asymmetry == UNKNOWN OR cost_matrix IS NULL:
        SET escalation_required = True
        escalation_reasons.append("COST_MATRIX_REQUIRED_TIER1_AUTOMATED_NOT_RESOLVED")

# Rule V7: Fairness sensitivity HIGH must have regulatory_mode != STANDARD
IF fairness_sensitivity == HIGH AND regulatory_mode == STANDARD:
    regulatory_mode = REGULATED
    conservative_overrides_applied.append("regulatory_mode_elevated_fairness_high")
```

---

## Qualitative Phrase Mapping Table

For open-text answer fields or ambiguous selections, map phrases to enum values:

```
RISK_TIER PHRASE MAP:
  "fully automated decision"          → TIER_1
  "no human review"                   → TIER_1
  "affects customers directly"        → TIER_1
  "internal recommendation"           → TIER_2
  "analyst reviews output"            → TIER_2
  "reports only"                      → TIER_3
  "research"                          → TIER_3
  "dashboard"                         → TIER_3

REGULATORY_MODE PHRASE MAP:
  "GDPR"                              → GDPR_STRICT
  "data protection"                   → GDPR_STRICT
  "SR 11-7" / "model risk"           → REGULATED
  "Basel" / "capital requirements"    → REGULATED
  "HIPAA" / "clinical"               → REGULATED
  "FCA" / "PRA" / "OCC"             → REGULATED
  "internal only"                     → STANDARD
  "no regulation"                     → STANDARD

INTERPRETABILITY PHRASE MAP:
  "explainable to customers"          → 1
  "black box is fine"                 → 3
  "regulator must understand"         → 1
  "complex model acceptable"          → 2 or 3 depending on risk_tier
  "scorecard required"                → 1
```

---

## Default Conservative Mapping (applied when inference confidence == LOW)

```
risk_tier:              TIER_1
interpretability_tier:  1
regulatory_mode:        REGULATED
deployment_mode:        HUMAN_REVIEWED
fairness_sensitivity:   HIGH
time_awareness:         NONE
cost_asymmetry:         SYMMETRIC
explanation_requirement: AUDIT_FACING
gdpr_art22_flag:        False
```
