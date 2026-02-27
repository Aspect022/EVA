# QuestionBuilderRules.md
## Enterprise Question Builder — Backend Governance Specification

**Version:** 3.0
**Status:** ENTERPRISE — Deterministic Governance Engine
**Reads:** `DatasetIdentity` (from GAL, produced by DomainAnalysisRules)
**Produces:** `RawAnswerRecord` → consumed by IntentInferenceRules
**Constraint:** Maximum 5 questions. No exceptions. No algorithm-specific language.

---

## SECTION 0 — Governance Preamble

1. This file is a **deterministic governance specification**. Question selection is rule-driven, not probabilistic.
2. **MAXIMUM QUESTION POLICY:**
   - This engine may issue a maximum of 5 questions per session.
   - All questions must be SINGLE_SELECT MCQ format.
   - MULTI_SELECT question types are prohibited.
   - FREE_TEXT responses are prohibited.
   - No additional clarification blocks may be prepended.
   - Question count must be deterministic and bounded.
3. No question may be skipped without a **recorded gate reason** in `RawAnswerRecord.gate_skip_reasons`.
4. Every output field in `RawAnswerRecord` must contain an enum value from `SECTION 1 — Enum Registry` or a Boolean. `NULL` is never a valid output for a governed field.
5. **Conservative fallback is mandatory on ambiguity.** If a gate cannot be evaluated (e.g., required DatasetIdentity field is UNKNOWN), the conservative fallback from `SECTION 5` applies. The corresponding question is issued.
6. All enum values produced by question answer mapping must match values declared in `SECTION 1` exactly.
7. **RAG is advisory only.** RAG context may not alter question gates, question text, or option mappings.

---

## SECTION 1 — Enum Registry

All enum values produced by this engine. Sourced from `DataScienceRules.md §Global Constants` and confirmed in `IntentInferenceRules.md SECTION 1`.

| Field | Legal Values |
|---|---|
| `primary_objective` | `PREDICT` \| `EXPLAIN` \| `SEGMENT` \| `ANOMALY_DETECT` \| `FORECAST` |
| `deployment_mode` | `AUTOMATED` \| `HUMAN_REVIEWED` \| `HYBRID` |
| `risk_tier` | `TIER_1` \| `TIER_2` \| `TIER_3` |
| `decision_impact` | `FINANCIAL_INDIVIDUAL` \| `HEALTH_SAFETY` \| `LEGAL_STATUS` \| `OPERATIONAL` \| `ANALYTICAL` |
| `explanation_requirement` | `INDIVIDUAL_FACING` \| `AUDIT_FACING` \| `BOTH` \| `NONE` |
| `error_cost_direction` | `FN_DOMINANT` \| `FP_DOMINANT` \| `SYMMETRIC` \| `UNKNOWN` |
| `cost_asymmetry` | `HIGH` \| `LOW` \| `UNKNOWN` |
| `fairness_sensitivity` | `HIGH` \| `MODERATE` \| `LOW` |
| `fairness_reporting_required` | `Boolean` |
| `regulatory_mode` | `STANDARD` \| `REGULATED` \| `GDPR_STRICT` |
| `regulatory_frameworks` | `SR_11_7` \| `GDPR` \| `SECTOR_CLINICAL` \| `MULTI` \| `INTERNAL` \| `NONE` |
| `time_awareness` | `FORECAST` \| `POINT_IN_TIME_STRICT` \| `TREND_ANALYSIS` \| `NONE` |
| `temporal_split_required` | `Boolean` |
| `gdpr_art22_flag` | `Boolean` |
| `interpretability_tier` | `1` \| `2` \| `3` |

---

## SECTION 2 — Input Contract

Fields read from `DatasetIdentity` in GAL before question generation begins:

```
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
  escalation_triggers:      [codes from DomainAnalysisRules SECTION 6]
```

> If any `DatasetIdentity` field required by a gate is `UNKNOWN`, the QuestionBuilder MUST issue the corresponding clarifying question rather than skipping it.

---

## SECTION 3 — Governance Precedence Hierarchy

```
Level 1 (Highest): HARD_STOP
  → Triggered only by SECTION 6 escalation conditions.
  → RawAnswerRecord is NOT written. Pipeline halted.

Level 2: Escalation Trigger
  → Applied when gate evaluation is ambiguous.
  → Question is issued and conservative fallback pre-set.
  → ambiguity_flag recorded in RawAnswerRecord.ambiguity_flags.

Level 3: Conservative Fallback
  → Applied when gate cannot be evaluated (DatasetIdentity field is UNKNOWN).
  → Fallback value applied from SECTION 5. Question is issued.

Level 4 (Lowest): Normal Issue
  → Gate condition is TRUE. Question issued. Answer determines output enum.
```

> No question may be omitted without a recorded gate reason (Level 3 or higher).

## QUESTION ROUTING MATRIX

Formal gate table. All conditions evaluated against current session state at time of question evaluation.

| Q# | GATE CONDITION (Issue if TRUE) | SKIP CONDITION (Skip if TRUE) | FIELDS PRODUCED | ENUMS PRODUCED |
|---|---|---|---|---|
| Q1 | Always | Never | `primary_objective` | `PREDICT`, `EXPLAIN`, `SEGMENT`, `ANOMALY_DETECT`, `FORECAST` |
| Q2 | `primary_objective IN [PREDICT, FORECAST, ANOMALY_DETECT]` | `primary_objective IN [EXPLAIN, SEGMENT]` | `deployment_mode` | `AUTOMATED`, `HUMAN_REVIEWED`, `HYBRID` |
| Q3 | `deployment_mode IN [AUTOMATED, HYBRID]` | `deployment_mode == HUMAN_REVIEWED AND domain_risk_flag == LOW` | `decision_impact`, `risk_tier` | `FINANCIAL_INDIVIDUAL`, `HEALTH_SAFETY`, `LEGAL_STATUS`, `OPERATIONAL`, `ANALYTICAL`; `TIER_1`, `TIER_2`, `TIER_3` |
| Q4 | `primary_objective == PREDICT AND deployment_mode IN [AUTOMATED, HYBRID]` | `primary_objective IN [SEGMENT, EXPLAIN, FORECAST]` | `error_cost_direction`, `cost_asymmetry` | `FN_DOMINANT`, `FP_DOMINANT`, `SYMMETRIC`, `UNKNOWN`; `HIGH`, `LOW`, `UNKNOWN` |
| Q5 | `has_temporal_column == True OR dataset_type IN [TIME_SERIES, PANEL] OR primary_objective == FORECAST` | `dataset_type == TABULAR AND has_temporal_column == False AND primary_objective != FORECAST` | `time_awareness`, `temporal_split_required` | `FORECAST`, `POINT_IN_TIME_STRICT`, `TREND_ANALYSIS`, `NONE` |

---

---

## SECTION 4 — Question Blocks

### Q1 — Business Objective Classification

**Gate:** Always issued. No conditions.

```
QUESTION:
  "What is the primary goal of this analysis?
   a) Predict a specific outcome for new or future records
   b) Understand which factors most influence an outcome
   c) Group or segment records by similarity
   d) Detect unusual or anomalous records
   e) Forecast future values over time"

QUESTION_TYPE: SINGLE_SELECT
RATIONALE: Determines prediction_vs_explanation_vs_segmentation gate.
           Routes to DRIL objective classification.
           Controls whether target column, label type, and threshold logic apply downstream.
```

**Answer → Enum Mapping:**

| Option | `primary_objective` |
|---|---|
| a | `PREDICT` |
| b | `EXPLAIN` |
| c | `SEGMENT` |
| d | `ANOMALY_DETECT` |
| e | `FORECAST` |
| NULL | `PREDICT` (conservative fallback — see SECTION 5) |

---

### Q2 — Decision Impact and Deployment Mode

**Gate:** `primary_objective IN [PREDICT, FORECAST, ANOMALY_DETECT]`
**Skip:** `primary_objective IN [EXPLAIN, SEGMENT]`

```
QUESTION:
  "How will the model's output be used?
   a) Automatically trigger a decision or action with no human review
   b) Present a recommendation that a person reviews before acting
   c) Flag cases for further investigation — a person makes the final call
   d) Generate insights or reports for strategic review only"

QUESTION_TYPE: SINGLE_SELECT
RATIONALE: Determines deployment_mode enum.
           Controls interpretability_tier floor.
           Determines whether fallback_trigger_level and confidence gating apply.
```

**Answer → Enum Mapping:**

| Option | `deployment_mode` | `decision_impact_floor` |
|---|---|---|
| a | `AUTOMATED` | — |
| b | `HUMAN_REVIEWED` | — |
| c | `HYBRID` | — |
| d | `HUMAN_REVIEWED` | `ANALYTICAL` |
| NULL | `HUMAN_REVIEWED` (conservative fallback) | — |

---

### Q3 — Decision Impact Severity

**Gate:** `deployment_mode IN [AUTOMATED, HYBRID]`
**Skip:** `deployment_mode == HUMAN_REVIEWED AND domain_risk_flag == LOW`

```
QUESTION:
  "What type of outcome does this decision affect?
   a) Financial outcomes for individuals — such as credit, loans, or insurance eligibility
   b) Health, safety, or clinical outcomes for individuals
   c) Employment, benefits, or legal status of individuals
   d) Business operations, internal processes, or commercial decisions
   e) Research, analytics, or reporting with no direct individual impact"

QUESTION_TYPE: SINGLE_SELECT
RATIONALE: Determines risk_tier classification.
           Triggers regulatory_mode when a, b, or c selected.
           Controls interpretability_tier minimum floor.
           Flags protected population exposure.
```

**Answer → Enum Mapping:**

| Option | `decision_impact` | `risk_tier` |
|---|---|---|
| a | `FINANCIAL_INDIVIDUAL` | `TIER_1` |
| b | `HEALTH_SAFETY` | `TIER_1` |
| c | `LEGAL_STATUS` | `TIER_1` |
| d | `OPERATIONAL` | `TIER_2` |
| e | `ANALYTICAL` | `TIER_3` |
| NULL | domain-derived conservative (see SECTION 5) | `TIER_1` |

---

### Q4 — Error Cost Asymmetry

**Gate:** `primary_objective == PREDICT AND deployment_mode IN [AUTOMATED, HYBRID]`
**Skip:** `primary_objective IN [SEGMENT, EXPLAIN, FORECAST]`

```
QUESTION:
  "For this model's predictions, which type of error is more costly?
   a) Missing a true positive — failing to detect a fraud case, defaulting borrower, or at-risk patient
   b) Producing a false alarm — incorrectly flagging a good customer or healthy patient
   c) Both errors are roughly equally costly
   d) I need help quantifying this — I am not sure"

QUESTION_TYPE: SINGLE_SELECT
RATIONALE: Determines cost_matrix structure.
           Controls threshold optimization objective in DataScienceRules Module 9.
           Triggers cost-sensitive learning flag in Module 8.
           Asymmetric responses elevate risk_tier if decision_impact is FINANCIAL_INDIVIDUAL or HEALTH_SAFETY.
```

**Answer → Enum Mapping:**

| Option | `error_cost_direction` | `cost_asymmetry` | Notes |
|---|---|---|---|
| a | `FN_DOMINANT` | `HIGH` | |
| b | `FP_DOMINANT` | `HIGH` | |
| c | `SYMMETRIC` | `LOW` | |
| d | `UNKNOWN` | `UNKNOWN` | Triggers `ambiguity_cost_flag = True`; conservative fallback: `FN_DOMINANT` if domain IN [HEALTHCARE, BANKING] |
| NULL | `SYMMETRIC` | `LOW` | Q4 not issued: no cost-sensitive learning requirement |

---

### Q5 — Time Awareness and Decision Horizon

**Gate:** `has_temporal_column == True OR dataset_type IN [TIME_SERIES, PANEL] OR primary_objective == FORECAST`
**Skip:** `dataset_type == TABULAR AND has_temporal_column == False AND primary_objective != FORECAST`

```
QUESTION:
  "Does the timing of data matter for this model?
   a) Yes — the model predicts future values using historical sequences
   b) Yes — the model must only use data available at the time each decision was made,
      not information that came later
   c) Yes — we need to understand how outcomes or patterns change across time periods
   d) No — time ordering is not relevant to this analysis"

QUESTION_TYPE: SINGLE_SELECT
RATIONALE: Determines time_awareness_required flag.
           Triggers temporal split enforcement in DataScienceRules Module 6.
           Triggers temporal leakage detection in Module 2.
           Controls rolling window CV vs. standard CV routing.
```

**Answer → Enum Mapping:**

| Option | `time_awareness` | `temporal_split_required` | `gap_injection` |
|---|---|---|---|
| a | `FORECAST` | `True` | `True` |
| b | `POINT_IN_TIME_STRICT` | `True` | `True` |
| c | `TREND_ANALYSIS` | `True` | `False` |
| d | `NONE` | `False` | `False` |
| NULL (temporal dataset) | `POINT_IN_TIME_STRICT` (conservative fallback) | `True` | `True` |
| NULL (non-temporal dataset) | `NONE` | `False` | `False` |

---

## SECTION 5 — Conservative Fallback Table

Applied when a question is skipped due to ambiguous gate evaluation, or when an answer is NULL. All fallback values use enums from `SECTION 1`. Applied at Level 3 of Governance Precedence Hierarchy.

| Field | Conservative Fallback | Trigger Condition |
|---|---|---|
| `primary_objective` | `PREDICT` | Q1 answer is NULL |
| `deployment_mode` | `HUMAN_REVIEWED` | Q2 not issued or answer NULL |
| `decision_impact` | domain-derived: BANKING→`FINANCIAL_INDIVIDUAL`, HEALTHCARE→`HEALTH_SAFETY`, INSURANCE→`FINANCIAL_INDIVIDUAL`, GENERAL→`OPERATIONAL` | Q3 not issued or answer NULL |
| `risk_tier` | `TIER_1` | decision_impact unresolved when deployment_mode is AUTOMATED |
| `error_cost_direction` | `FN_DOMINANT` | Q4 answer == "d" AND domain IN [HEALTHCARE, BANKING] |
| `error_cost_direction` | `SYMMETRIC` | Q4 answer == "d" AND domain NOT IN [HEALTHCARE, BANKING] |
| `time_awareness` | `POINT_IN_TIME_STRICT` | Q5 not issued; has_temporal_column == True or dataset_type temporal |
| `time_awareness` | `NONE` | Q5 not issued; non-temporal dataset |
| `temporal_split_required` | `True` | time_awareness is POINT_IN_TIME_STRICT or FORECAST |

---

## SECTION 6 — Escalation Registry

All escalation conditions triggered by this engine. Written to `RawAnswerRecord.ambiguity_flags`.

| CODE | TRIGGER CONDITION | SEVERITY | ACTION | SLA | DOWNSTREAM EFFECT |
|---|---|---|---|---|---|
| `PREDICT_NO_TARGET_COLUMN` | `primary_objective == PREDICT AND DatasetIdentity.has_target_column == False` | HARD_STOP | HALT_PIPELINE_REQUIRE_HUMAN_RESOLUTION | Immediate | RawAnswerRecord NOT written |

---

## SECTION 7 — Validation Rules

Run after all questions are issued and answered, before `RawAnswerRecord` is written.

```python
# V1: primary_objective must be resolved to a legal enum
ASSERT primary_objective IN [PREDICT, EXPLAIN, SEGMENT, ANOMALY_DETECT, FORECAST]

# V2: SEGMENT and EXPLAIN cannot have deployment_mode == AUTOMATED
IF primary_objective IN [SEGMENT, EXPLAIN] AND deployment_mode == AUTOMATED:
    deployment_mode = HUMAN_REVIEWED
    conservative_fallbacks_applied.append("deployment_mode_corrected_non_predictive")

# V3: FORECAST objective must have temporal_split_required = True
IF primary_objective == FORECAST AND temporal_split_required == False:
    temporal_split_required = True
    conservative_fallbacks_applied.append("temporal_split_enforced_forecast")

# V4: QUESTION POLICY ENFORCEMENT
ASSERT len(questions_issued) <= 5
ASSERT all(question_type == SINGLE_SELECT)
```

---

## SECTION 8 — Output Contract

`RawAnswerRecord` produced by this engine, passed to IntentInferenceRules:

```
RawAnswerRecord:
  session_id:                       UUID
  dataset_identity_ref:             DatasetIdentity.id from GAL
  questions_issued:                 [Q1-Q5] list of issued question IDs
  answers:                          {Q1-Q5: selected_option}
  gate_skip_reasons:                {Q#: "reason string"} for every skipped question
  ambiguity_flags:                  {flag_code: Boolean} from SECTION 6
  conservative_fallbacks_applied:   [list of field names where fallback used]
  timestamp:                        ISO timestamp
```
