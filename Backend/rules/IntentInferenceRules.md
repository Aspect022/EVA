# IntentInferenceRules.md
## Enterprise Intent Inference Engine — Backend Governance Specification

**Version:** 3.0
**Status:** ENTERPRISE — Deterministic Governance Engine
**Reads:** `RawAnswerRecord` (from QuestionBuilderRules), `DatasetIdentity` (from GAL)
**Produces:** `UserIntentRecord` → consumed by DRIL, EPR, DataScienceRules engine
**Constraint:** All output fields must map to exact enum values in `DataScienceRules.md`

---

## SECTION 0 — Governance Preamble

1. This file is a **deterministic governance specification**. All inference is rule-driven. No probabilistic override is permitted.
2. All output enum values must exactly match values declared in `SECTION 1 — Enum Registry`. No other values may appear in any `UserIntentRecord` field.
3. This engine is the **sole authority** for producing `UserIntentRecord`. No agent may write directly to `UserIntentRecord` bypassing this engine.
4. **Conservative overrides are mandatory on any ambiguity.** If an inference cannot be resolved, the conservative fallback from `SECTION 5` must apply and must be logged in `conservative_overrides_applied`.
5. **RAG is advisory only.** RAG context must never alter any inferred field in `UserIntentRecord`.
6. `UserIntentRecord` is NOT written to GAL if `escalation_required == True` AND the triggering condition is classified as `HARD_STOP` in `SECTION 6`.
7. Risk tier can only be **elevated** during this engine's execution — never lowered by any downstream override.

---

## SECTION 1 — Enum Registry

All enum values produced by this engine. Sourced from `DataScienceRules.md §Global Constants`. No values outside this registry may appear in any `UserIntentRecord` field.

| Field | Legal Values |
|---|---|
| `primary_objective` | `PREDICT` \| `EXPLAIN` \| `SEGMENT` \| `ANOMALY_DETECT` \| `FORECAST` |
| `deployment_mode` | `AUTOMATED` \| `HUMAN_REVIEWED` \| `HYBRID` |
| `decision_impact` | `FINANCIAL_INDIVIDUAL` \| `HEALTH_SAFETY` \| `LEGAL_STATUS` \| `OPERATIONAL` \| `ANALYTICAL` |
| `risk_tier` | `TIER_1` \| `TIER_2` \| `TIER_3` |
| `interpretability_tier` | `1` \| `2` \| `3` |
| `regulatory_mode` | `STANDARD` \| `REGULATED` \| `GDPR_STRICT` |
| `regulatory_frameworks` | `SR_11_7` \| `GDPR` \| `SECTOR_CLINICAL` \| `MULTI` \| `INTERNAL` \| `NONE` |
| `domain_override` | `BANKING` \| `HEALTHCARE` \| `INSURANCE` \| `GENERAL` \| `NULL` |
| `error_cost_direction` | `FN_DOMINANT` \| `FP_DOMINANT` \| `SYMMETRIC` \| `UNKNOWN` |
| `cost_asymmetry` | `HIGH` \| `LOW` \| `UNKNOWN` |
| `fairness_sensitivity` | `HIGH` \| `MODERATE` \| `LOW` |
| `time_awareness` | `FORECAST` \| `POINT_IN_TIME_STRICT` \| `TREND_ANALYSIS` \| `NONE` |
| `explanation_requirement` | `INDIVIDUAL_FACING` \| `AUDIT_FACING` \| `BOTH` \| `NONE` |
| `inference_confidence` | `HIGH` \| `MEDIUM` \| `LOW` |

---

## SECTION 2 — Input Contract

```
RawAnswerRecord:
  session_id:                       UUID
  dataset_identity_ref:             DatasetIdentity.id
  questions_issued:                 [Q_IDs]
  answers:                          {Q_ID: selected_option}
  gate_skip_reasons:                {Q#: reason_string}
  ambiguity_flags:                  {flag_name: Boolean}
  conservative_fallbacks_applied:   [field_names]

DatasetIdentity:
  domain:                   BANKING | HEALTHCARE | INSURANCE | GENERAL | UNKNOWN
  dataset_type:             TABULAR | TIME_SERIES | PANEL | NLP | CV | GRAPH | UNKNOWN
  has_target_column:        Boolean
  has_temporal_column:      Boolean
  has_group_column:         Boolean
  has_pii_detected:         Boolean
  n_rows:                   Integer or UNKNOWN
  n_features:               Integer or UNKNOWN
  label_type:               BINARY | MULTICLASS | REGRESSION | NONE | UNKNOWN
  domain_risk_flag:         LOW | MODERATE | HIGH | CRITICAL
  regulatory_exposure_flag: Boolean
  protected_attribute_flag: Boolean
  escalation_triggers:      [codes]
```

---

## SECTION 3 — Governance Precedence Hierarchy

The following precedence stack is enforced at every inference block. A higher-priority outcome always supersedes a lower one.

```
Level 1 (Highest): HARD_STOP
  → UserIntentRecord is NOT written to GAL.
  → Triggered by SECTION 6 HARD_STOP conditions.

Level 2: Escalation Trigger
  → UserIntentRecord written WITH escalation_required = True and escalation_reasons populated.
  → Downstream modules must check escalation_required before processing.

Level 3: Domain-Based Conservative Default
  → Applied when Q answer is NULL and domain implies a regulated default.
  → Value logged in conservative_overrides_applied.

Level 4: Risk Tier Override
  → Risk tier elevation rules (see RISK_TIER_ELEVATION_MATRIX).
  → Tier can only be elevated, never lowered.

Level 5 (Lowest): Inferred Value
  → Normal deterministic inference from RawAnswerRecord.answers.
```

**Regulatory Mode Precedence (non-negotiable):**
```
GDPR_STRICT > REGULATED > STANDARD
```
Any logic path that would produce a lower-precedence mode when a higher one is already assigned must preserve the higher-precedence value.

---

## SECTION 4 — Inference Blocks

### BLOCK 1 — Primary Objective Inference

```python
answer_Q1 = RawAnswerRecord.answers.get("Q1")

IF answer_Q1 == "a":   primary_objective = PREDICT
ELIF answer_Q1 == "b": primary_objective = EXPLAIN
ELIF answer_Q1 == "c": primary_objective = SEGMENT
ELIF answer_Q1 == "d": primary_objective = ANOMALY_DETECT
ELIF answer_Q1 == "e": primary_objective = FORECAST
ELIF answer_Q1 IS NULL:
    primary_objective = PREDICT
    conservative_overrides_applied.append("primary_objective")
    inference_confidence = LOW

# Cross-check: FORECAST requires temporal dataset
IF primary_objective == FORECAST AND DatasetIdentity.dataset_type NOT IN [TIME_SERIES, PANEL]:
    inference_confidence = MEDIUM
    # SOFT_WARN: mismatch logged, no halt

# Cross-check: PREDICT requires target column
IF primary_objective == PREDICT AND DatasetIdentity.has_target_column == False:
    escalation_required = True
    escalation_reasons.append("PREDICT_NO_TARGET_COLUMN")
```

---

### BLOCK 2 — Deployment Mode Inference

```python
answer_Q2 = RawAnswerRecord.answers.get("Q2")

IF answer_Q2 == "a":   deployment_mode = AUTOMATED
ELIF answer_Q2 == "b": deployment_mode = HUMAN_REVIEWED
ELIF answer_Q2 == "c": deployment_mode = HYBRID
ELIF answer_Q2 == "d":
    deployment_mode = HUMAN_REVIEWED
    decision_impact_floor = ANALYTICAL
ELIF answer_Q2 IS NULL AND primary_objective IN [EXPLAIN, SEGMENT]:
    deployment_mode = HUMAN_REVIEWED
ELIF answer_Q2 IS NULL:
    deployment_mode = HUMAN_REVIEWED
    conservative_overrides_applied.append("deployment_mode")
```

---

### BLOCK 3 — Decision Impact and Risk Tier Inference

#### Answer Mapping

```python
answer_Q3 = RawAnswerRecord.answers.get("Q3")

impact_map = {
    "a": FINANCIAL_INDIVIDUAL,
    "b": HEALTH_SAFETY,
    "c": LEGAL_STATUS,
    "d": OPERATIONAL,
    "e": ANALYTICAL
}

IF answer_Q3 IS NOT NULL:
    decision_impact = impact_map[answer_Q3]
ELIF DatasetIdentity.domain == BANKING:
    decision_impact = FINANCIAL_INDIVIDUAL
    conservative_overrides_applied.append("decision_impact_banking_default")
ELIF DatasetIdentity.domain == HEALTHCARE:
    decision_impact = HEALTH_SAFETY
    conservative_overrides_applied.append("decision_impact_healthcare_default")
ELIF DatasetIdentity.domain == INSURANCE:
    decision_impact = FINANCIAL_INDIVIDUAL
    conservative_overrides_applied.append("decision_impact_insurance_default")
ELSE:
    decision_impact = OPERATIONAL
    conservative_overrides_applied.append("decision_impact_general_default")
```

#### RISK_TIER_ELEVATION_MATRIX

All risk tier elevation paths, in evaluation order. Tier can only increase.

| Condition | Resulting risk_tier | Override Logged |
|---|---|---|
| `decision_impact IN [FINANCIAL_INDIVIDUAL, HEALTH_SAFETY, LEGAL_STATUS]` | `TIER_1` (floor) | No |
| `decision_impact == OPERATIONAL` | `TIER_2` (floor) | No |
| `decision_impact == ANALYTICAL` | `TIER_3` (floor) | No |
| `deployment_mode == AUTOMATED AND risk_tier_floor == TIER_2` | Elevated to `TIER_1` | `risk_tier_automated_elevation` |
| `deployment_mode == HUMAN_REVIEWED AND risk_tier_floor == TIER_1` | Stays `TIER_1` (human review does not lower TIER_1) | No |
| `DatasetIdentity.domain_risk_flag == CRITICAL AND risk_tier_floor != TIER_1` | Elevated to `TIER_1` | `risk_tier_domain_critical_override` |

```python
# Apply elevation matrix (in sequence)
IF decision_impact IN [FINANCIAL_INDIVIDUAL, HEALTH_SAFETY, LEGAL_STATUS]:
    risk_tier_floor = TIER_1
ELIF decision_impact == OPERATIONAL:
    risk_tier_floor = TIER_2
ELSE:
    risk_tier_floor = TIER_3

IF deployment_mode == AUTOMATED AND risk_tier_floor == TIER_2:
    risk_tier_floor = TIER_1
    conservative_overrides_applied.append("risk_tier_automated_elevation")

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
    interpretability_tier_from_q4 = 1
    gdpr_art22_flag = True
ELIF answer_Q4 == "b":
    explanation_requirement = AUDIT_FACING
    interpretability_tier_from_q4 = 1
    gdpr_art22_flag = False
ELIF answer_Q4 == "c":
    explanation_requirement = BOTH
    interpretability_tier_from_q4 = 1
    gdpr_art22_flag = True
ELIF answer_Q4 == "d":
    explanation_requirement = NONE
    interpretability_tier_from_q4 = 2
    gdpr_art22_flag = False
ELIF answer_Q4 IS NULL:
    IF risk_tier == TIER_1:
        interpretability_tier_from_q4 = 1
        explanation_requirement = AUDIT_FACING
    ELIF risk_tier == TIER_2:
        interpretability_tier_from_q4 = 2
        explanation_requirement = NONE
    ELSE:
        interpretability_tier_from_q4 = 3
        explanation_requirement = NONE
    conservative_overrides_applied.append("interpretability_tier")

# Apply risk tier floor enforcement
IF risk_tier == TIER_1:
    interpretability_tier = min(1, interpretability_tier_from_q4)
ELIF risk_tier == TIER_2:
    interpretability_tier = min(2, interpretability_tier_from_q4)
ELSE:
    interpretability_tier = interpretability_tier_from_q4

# GDPR Art. 22 override — supersedes all other assignments
IF gdpr_art22_flag == True:
    interpretability_tier = 1

# Architecture cross-checks
IF DatasetIdentity.dataset_type == NLP AND interpretability_tier == 1:
    escalation_required = True
    escalation_reasons.append("NLP_INTERPRETABILITY_CONFLICT")

IF DatasetIdentity.dataset_type == CV AND interpretability_tier <= 2:
    escalation_required = True
    escalation_reasons.append("CV_INTERPRETABILITY_CONFLICT")
```

---

### BLOCK 5 — Regulatory Mode Inference

#### REGULATORY_MODE_PRECEDENCE_TABLE

Precedence rule: `GDPR_STRICT > REGULATED > STANDARD`. Once a higher-precedence mode is assigned, it cannot be lowered by any subsequent block.

| Trigger | `regulatory_mode` | `regulatory_frameworks` |
|---|---|---|
| Q7 answer includes "b" (GDPR) or "d" (MULTI) | `GDPR_STRICT` | `[GDPR]` or `[MULTI]` |
| Q7 answer includes "a" (SR_11_7) | `REGULATED` | `[SR_11_7]` |
| Q7 answer includes "c" (SECTOR_CLINICAL) | `REGULATED` | `[SECTOR_CLINICAL]` |
| Q7 answer includes "e" (INTERNAL) | `STANDARD` | `[INTERNAL]` |
| Q7 answer includes "f" (NONE) | `STANDARD` | `[]` |
| Q7 NULL AND domain == BANKING | `REGULATED` | `[SR_11_7]` |
| Q7 NULL AND domain == HEALTHCARE | `REGULATED` | `[SECTOR_CLINICAL]` |
| Q7 NULL AND domain == INSURANCE | `REGULATED` | `[SECTOR_CLINICAL]` |
| Q7 NULL AND risk_tier == TIER_1 | `REGULATED` | `[INTERNAL]` |
| Q7 NULL AND all other cases | `STANDARD` | `[NONE]` |
| `deployment_mode == AUTOMATED AND risk_tier == TIER_1 AND mode == STANDARD` | Elevated to `REGULATED` | logged |
| `gdpr_art22_flag == True AND mode == STANDARD` | Elevated to `GDPR_STRICT` | logged |
| `fairness_sensitivity == HIGH AND mode == STANDARD` | Elevated to `REGULATED` | logged |

```python
answer_Q7 = RawAnswerRecord.answers.get("Q7")

IF answer_Q7 IS NOT NULL:
    selected_options = answer_Q7  # multi-select list

    IF "b" IN selected_options OR "d" IN selected_options:
        regulatory_mode = GDPR_STRICT
    ELIF "a" IN selected_options OR "c" IN selected_options:
        regulatory_mode = REGULATED
    ELIF "e" IN selected_options:
        regulatory_mode = STANDARD
    ELIF "f" IN selected_options:
        regulatory_mode = STANDARD
    ELSE:
        regulatory_mode = STANDARD

    framework_map = {
        "a": SR_11_7, "b": GDPR, "c": SECTOR_CLINICAL,
        "d": MULTI, "e": INTERNAL, "f": NONE
    }
    regulatory_frameworks = [framework_map[o] for o in selected_options]

ELSE:
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

# Apply precedence elevation rules (GDPR_STRICT > REGULATED > STANDARD)
IF deployment_mode == AUTOMATED AND risk_tier == TIER_1 AND regulatory_mode == STANDARD:
    regulatory_mode = REGULATED
    conservative_overrides_applied.append("regulatory_mode_automated_tier1_escalation")

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
    cost_matrix = {FP_cost_relative: 1.0, FN_cost_relative: 5.0, cost_asymmetry: HIGH}

ELIF answer_Q5 == "b":
    error_cost_direction = FP_DOMINANT
    cost_asymmetry = HIGH
    cost_matrix = {FP_cost_relative: 5.0, FN_cost_relative: 1.0, cost_asymmetry: HIGH}

ELIF answer_Q5 == "c":
    error_cost_direction = SYMMETRIC
    cost_asymmetry = LOW
    cost_matrix = {FP_cost_relative: 1.0, FN_cost_relative: 1.0, cost_asymmetry: LOW}

ELIF answer_Q5 == "d":
    error_cost_direction = UNKNOWN
    cost_asymmetry = UNKNOWN
    # Domain-based conservative fallback
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
    ambiguity_flags["COST_MATRIX_UNKNOWN"] = True

ELIF answer_Q5 IS NULL:
    error_cost_direction = SYMMETRIC
    cost_asymmetry = LOW
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
    IF DatasetIdentity.protected_attribute_flag == True:
        fairness_sensitivity = MODERATE
        conservative_overrides_applied.append("fairness_sensitivity_pii_default")
    ELIF DatasetIdentity.domain IN [BANKING, HEALTHCARE, INSURANCE]:
        fairness_sensitivity = MODERATE
        conservative_overrides_applied.append("fairness_sensitivity_domain_default")
    ELSE:
        fairness_sensitivity = LOW
    fairness_reporting_required = False

# Apply regulatory elevation from fairness (GDPR_STRICT > REGULATED > STANDARD)
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
    IF DatasetIdentity.dataset_type IN [TIME_SERIES, PANEL] OR DatasetIdentity.has_temporal_column == True:
        time_awareness = POINT_IN_TIME_STRICT
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
user_implied_domain = NULL

IF decision_impact == FINANCIAL_INDIVIDUAL AND DatasetIdentity.domain NOT IN [BANKING, INSURANCE]:
    user_implied_domain = BANKING
ELIF decision_impact == HEALTH_SAFETY AND DatasetIdentity.domain != HEALTHCARE:
    user_implied_domain = HEALTHCARE

# Governance rule: user intent overrides automated domain detection when DatasetIdentity.domain
# is GENERAL or UNKNOWN and decision_impact implies a regulated domain.
IF user_implied_domain IS NOT NULL AND DatasetIdentity.domain != UNKNOWN:
    IF user_implied_domain != DatasetIdentity.domain:
        domain_conflict_flag = True
        domain_override = user_implied_domain
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

IF ambiguity_flags.get("COST_MATRIX_UNKNOWN") == True:
    confidence_deductions += 1

IF conservative_overrides_applied.count > 3:
    confidence_deductions += 1

IF escalation_required == True:
    confidence_deductions += 2

IF domain_conflict_flag == True:
    confidence_deductions += 1

IF DatasetIdentity.domain == UNKNOWN:
    confidence_deductions += 1

IF confidence_deductions == 0:      inference_confidence = HIGH
ELIF confidence_deductions <= 2:    inference_confidence = MEDIUM
ELSE:                               inference_confidence = LOW
```

---

## SECTION 5 — Conservative Fallback Table

Applied when inference cannot resolve a governed field. All fallback values use enums from `SECTION 1`. Logged in `conservative_overrides_applied`.

| Field | Conservative Fallback | Trigger Condition |
|---|---|---|
| `primary_objective` | `PREDICT` | Q1 answer NULL |
| `deployment_mode` | `HUMAN_REVIEWED` | Q2 not issued or NULL |
| `decision_impact` | `FINANCIAL_INDIVIDUAL` | domain == BANKING or INSURANCE, Q3 NULL |
| `decision_impact` | `HEALTH_SAFETY` | domain == HEALTHCARE, Q3 NULL |
| `decision_impact` | `OPERATIONAL` | domain == GENERAL, Q3 NULL |
| `risk_tier` | `TIER_1` | decision_impact unresolved on AUTOMATED deployment |
| `interpretability_tier` | `1` | Q4 NULL and risk_tier == TIER_1 |
| `explanation_requirement` | `AUDIT_FACING` | Q4 NULL and risk_tier == TIER_1 |
| `regulatory_mode` | `REGULATED` | Q7 NULL AND (domain regulated OR risk_tier == TIER_1) |
| `regulatory_mode` | `STANDARD` | Q7 NULL AND domain == GENERAL AND risk_tier == TIER_3 |
| `fairness_sensitivity` | `MODERATE` | Q6 NULL AND protected_attribute_flag == True |
| `error_cost_direction` | `FN_DOMINANT` | Q5 == "d" AND domain IN [HEALTHCARE, BANKING] |
| `error_cost_direction` | `SYMMETRIC` | Q5 == "d" AND domain not in regulated set |
| `time_awareness` | `POINT_IN_TIME_STRICT` | Q8 NULL AND temporal dataset detected |
| `inference_confidence` | `LOW` | confidence_deductions > 2 |

---

## SECTION 6 — Escalation Registry

All escalation conditions triggered by this engine. Written to `UserIntentRecord.escalation_reasons` when triggered.

| CODE | TRIGGER CONDITION | SEVERITY | ACTION | SLA | DOWNSTREAM EFFECT |
|---|---|---|---|---|---|
| `PREDICT_NO_TARGET_COLUMN` | `primary_objective == PREDICT AND DatasetIdentity.has_target_column == False` | HARD_STOP | HALT_PIPELINE_REQUIRE_HUMAN_RESOLUTION | Immediate | UserIntentRecord NOT written to GAL |
| `NLP_INTERPRETABILITY_CONFLICT` | `DatasetIdentity.dataset_type == NLP AND interpretability_tier == 1` | HARD_STOP | HALT_PIPELINE_REQUIRE_USE_CASE_SCOPE_REVISION | Immediate | UserIntentRecord NOT written to GAL |
| `CV_INTERPRETABILITY_CONFLICT` | `DatasetIdentity.dataset_type == CV AND interpretability_tier <= 2` | HARD_STOP | HALT_PIPELINE_REQUIRE_USE_CASE_SCOPE_REVISION | Immediate | UserIntentRecord NOT written to GAL |
| `GDPR_ART22_EXPLANATION_REQUIRED_NOT_CONFIGURED` | `deployment_mode == AUTOMATED AND risk_tier == TIER_1 AND explanation_requirement == NONE AND gdpr_art22_flag == True` | HARD_STOP | HALT_PIPELINE_REQUIRE_COMPLIANCE_REVIEW | Immediate | UserIntentRecord NOT written to GAL |
| `LOW_CONFIDENCE_TIER1_INFERENCE` | `inference_confidence == LOW AND risk_tier == TIER_1` | SOFT_WARN | ESCALATE_TO_MODEL_RISK_BEFORE_PROCEEDING | 24h | UserIntentRecord written; downstream must check |
| `COST_MATRIX_REQUIRED_TIER1_AUTOMATED_NOT_RESOLVED` | `risk_tier == TIER_1 AND deployment_mode == AUTOMATED AND cost_asymmetry == UNKNOWN` | SOFT_WARN | NOTIFY_ML_LEAD_FOR_COST_MATRIX_REVIEW | 48h | UserIntentRecord written with flag |
| `DOMAIN_OVERRIDE_CONFLICT` | `domain_conflict_flag == True AND domain_override IS NOT NULL` | SOFT_WARN | LOG_DOMAIN_OVERRIDE_FOR_AUDIT | — | domain_override field populated in UserIntentRecord |

---

## SECTION 7 — Validation Rules

Run after all inference blocks complete, before `UserIntentRecord` is written to GAL.

```python
# V1: AUTOMATED + TIER_1 must have interpretability_tier = 1
IF deployment_mode == AUTOMATED AND risk_tier == TIER_1:
    IF interpretability_tier != 1:
        interpretability_tier = 1
        conservative_overrides_applied.append("interpretability_enforced_automated_tier1")

# V2: GDPR_STRICT requires gdpr_art22_flag or individual-facing explanation
IF regulatory_mode == GDPR_STRICT:
    IF gdpr_art22_flag == False AND explanation_requirement == NONE \
       AND decision_impact IN [FINANCIAL_INDIVIDUAL, HEALTH_SAFETY, LEGAL_STATUS]:
        gdpr_art22_flag = True
        explanation_requirement = INDIVIDUAL_FACING
        conservative_overrides_applied.append("gdpr_art22_flag_enforced_strict_mode")

# V3: FORECAST requires temporal_split_required = True
IF primary_objective == FORECAST:
    IF temporal_split_required == False:
        temporal_split_required = True
        conservative_overrides_applied.append("temporal_split_enforced_forecast_objective")

# V4: SEGMENT and EXPLAIN cannot be AUTOMATED
IF primary_objective IN [SEGMENT, EXPLAIN] AND deployment_mode == AUTOMATED:
    deployment_mode = HUMAN_REVIEWED
    conservative_overrides_applied.append("deployment_mode_corrected_non_predictive_objective")

# V5: ANOMALY_DETECT should default to HYBRID if deployment_mode is AUTOMATED
IF primary_objective == ANOMALY_DETECT AND deployment_mode == AUTOMATED:
    deployment_mode = HYBRID
    conservative_overrides_applied.append("deployment_mode_anomaly_detect_hybrid_default")

# V6: Cost matrix must exist for TIER_1 AUTOMATED deployments
IF risk_tier == TIER_1 AND deployment_mode == AUTOMATED:
    IF cost_asymmetry == UNKNOWN OR cost_matrix IS NULL:
        escalation_required = True
        escalation_reasons.append("COST_MATRIX_REQUIRED_TIER1_AUTOMATED_NOT_RESOLVED")

# V7: fairness_sensitivity HIGH must have regulatory_mode != STANDARD
IF fairness_sensitivity == HIGH AND regulatory_mode == STANDARD:
    regulatory_mode = REGULATED
    conservative_overrides_applied.append("regulatory_mode_elevated_fairness_high")

# V8: All enum fields must contain legal values (final assertion)
ASSERT primary_objective IN [PREDICT, EXPLAIN, SEGMENT, ANOMALY_DETECT, FORECAST]
ASSERT deployment_mode IN [AUTOMATED, HUMAN_REVIEWED, HYBRID]
ASSERT risk_tier IN [TIER_1, TIER_2, TIER_3]
ASSERT regulatory_mode IN [STANDARD, REGULATED, GDPR_STRICT]
ASSERT inference_confidence IN [HIGH, MEDIUM, LOW]
```

---

## SECTION 8 — Output Contract

`UserIntentRecord` produced by this engine:

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
  regulatory_frameworks:    [SR_11_7 | GDPR | SECTOR_CLINICAL | MULTI | INTERNAL | NONE]
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
  escalation_reasons:       [list of codes from SECTION 6]
  conservative_overrides_applied: [list of field names]
  timestamp:                ISO timestamp
```

---

## SECTION 9 — GAL Write Specification

Field-by-field mapping from engine output to `UserIntentRecord` Pydantic model in `gal_schema.py`.

| Engine Field | `gal_schema.py` Field | Type | Notes |
|---|---|---|---|
| `primary_objective` | `UserIntentRecord.primary_objective` | `str` | Must match SECTION 1 enum |
| `deployment_mode` | `UserIntentRecord.deployment_mode` | `str` | Must match SECTION 1 enum |
| `decision_impact` | `UserIntentRecord.decision_impact` | `str` | Must match SECTION 1 enum |
| `risk_tier` | `UserIntentRecord.risk_tier` | `str` | Must match SECTION 1 enum |
| `interpretability_tier` | `UserIntentRecord.interpretability_tier` | `int \| str` | Values: 1, 2, 3 |
| `regulatory_mode` | `UserIntentRecord.regulatory_mode` | `str` | Must match SECTION 1 enum |
| `regulatory_frameworks` | `UserIntentRecord.regulatory_frameworks` | `List[str]` | Coerced from str if needed |
| `domain_override` | `UserIntentRecord.domain_override` | `Optional[str]` | NULL if no override |
| `cost_matrix` | `UserIntentRecord.cost_matrix` | `CostMatrix \| Dict` | |
| `error_cost_direction` | `UserIntentRecord.error_cost_direction` | `str` | |
| `fairness_sensitivity` | `UserIntentRecord.fairness_sensitivity` | `str` | |
| `fairness_reporting_required` | `UserIntentRecord.fairness_reporting_required` | `bool` | |
| `time_awareness` | `UserIntentRecord.time_awareness` | `str` | |
| `temporal_split_required` | `UserIntentRecord.temporal_split_required` | `bool` | |
| `explanation_requirement` | `UserIntentRecord.explanation_requirement` | `str` | |
| `gdpr_art22_flag` | `UserIntentRecord.gdpr_art22_flag` | `bool` | |
| `inference_confidence` | `UserIntentRecord.inference_confidence` | `str` | |
| `escalation_required` | `UserIntentRecord.escalation_required` | `bool` | |
| `escalation_reasons` | `UserIntentRecord.escalation_reasons` | `List[str]` | |
| `conservative_overrides_applied` | `UserIntentRecord.conservative_overrides_applied` | `List[str]` | |

```python
# HARD_STOP gate: do not write if any HARD_STOP escalation is active
IF any(code in escalation_reasons for code in [
    "PREDICT_NO_TARGET_COLUMN",
    "NLP_INTERPRETABILITY_CONFLICT",
    "CV_INTERPRETABILITY_CONFLICT",
    "GDPR_ART22_EXPLANATION_REQUIRED_NOT_CONFIGURED"
]):
    RETURN HARD_STOP
    reason = "HARD_STOP escalation active. UserIntentRecord will not be written to GAL."

WRITE UserIntentRecord TO GAL
RETURN UserIntentRecord.session_id
```
