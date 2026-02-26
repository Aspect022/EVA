# QuestionBuilderRules.md
## Enterprise Question Builder — Backend Governance Specification
**Version:** 2.0
**Feeds:** UserIntentRecord → IntentInferenceRules → DRIL / EPR / DataScienceRules engine
**Reads:** DatasetIdentity (from GAL, produced by DomainAnalysisRules)
**Constraint:** Maximum 5–8 questions per session. No algorithm-specific language.

---

## Global Constraints

```
MAX_QUESTIONS = 8
MIN_QUESTIONS = 5
OUTPUT_FORMAT_REQUIRED = {question, question_type, why_asked}
NO_ALGORITHM_LANGUAGE = True
CONSERVATIVE_FALLBACK = True
AMBIGUITY_DETECTION = True
```

---

## Input Contract

The QuestionBuilder receives the following from GAL before generating any question:

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
```

If any DatasetIdentity field is UNKNOWN, the QuestionBuilder MUST include a clarifying question that resolves that field before downstream questions that depend on it.

---

## Pre-Question Gate: Ambiguity Detection

Run before question sequence begins.

```python
IF DatasetIdentity.domain == UNKNOWN:
    PREPEND Question Block A (Domain Clarification)
    ambiguity_flag = True

IF DatasetIdentity.dataset_type == UNKNOWN:
    PREPEND Question Block B (Dataset Structure Clarification)
    ambiguity_flag = True

IF DatasetIdentity.label_type == NONE AND DatasetIdentity.has_target_column == False:
    SET use_case_scope = UNSUPERVISED_OR_EXPLORATORY
    SKIP questions requiring label assumptions (Q3, Q4, Q7)

IF DatasetIdentity.n_rows == UNKNOWN OR DatasetIdentity.n_rows < 100:
    PREPEND soft warning to session context:
    "Dataset may be too small for reliable predictive modeling. Questions will proceed but outputs may be flagged."
```

---

## Question Sequence

Questions are numbered Q1–Q8. Conditional gates determine which questions are issued per session. Not all questions fire in every session.

---

### Q1 — Business Objective Classification
**Always issued. No conditions.**

```
question:
  "What is the primary goal of this analysis?
   a) Predict a specific outcome for new or future records
   b) Understand which factors most influence an outcome
   c) Group or segment records by similarity
   d) Detect unusual or anomalous records
   e) Forecast future values over time"

question_type: SINGLE_SELECT

why_asked:
  Determines prediction_vs_explanation_vs_segmentation gate.
  Routes to DRIL objective classification.
  Controls whether target column, label type, and threshold logic apply downstream.
  Maps to: UserIntentRecord.primary_objective
```

**Output mapping:**
```
a → objective = PREDICT
b → objective = EXPLAIN
c → objective = SEGMENT
d → objective = ANOMALY_DETECT
e → objective = FORECAST
```

---

### Q2 — Decision Impact and Deployment Mode
**Gate: Issue if objective IN [PREDICT, FORECAST, ANOMALY_DETECT]**
**Skip if objective IN [EXPLAIN, SEGMENT]**

```
question:
  "How will the model's output be used?
   a) Automatically trigger a decision or action with no human review
   b) Present a recommendation that a person reviews before acting
   c) Flag cases for further investigation — a person makes the final call
   d) Generate insights or reports for strategic review only"

question_type: SINGLE_SELECT

why_asked:
  Determines deployment_mode enum.
  Controls interpretability_tier floor.
  Determines whether fallback_trigger_level and confidence gating apply.
  Maps to: UserIntentRecord.deployment_mode
```

**Output mapping:**
```
a → deployment_mode = AUTOMATED
b → deployment_mode = HUMAN_REVIEWED
c → deployment_mode = HYBRID
d → deployment_mode = HUMAN_REVIEWED, decision_impact = ANALYTICAL
```

---

### Q3 — Decision Impact Severity
**Gate: Issue if deployment_mode IN [AUTOMATED, HYBRID]**
**Skip if deployment_mode == HUMAN_REVIEWED AND domain_risk_flag == LOW**

```
question:
  "What type of outcome does this decision affect?
   a) Financial outcomes for individuals — such as credit, loans, or insurance eligibility
   b) Health, safety, or clinical outcomes for individuals
   c) Employment, benefits, or legal status of individuals
   d) Business operations, internal processes, or commercial decisions
   e) Research, analytics, or reporting with no direct individual impact"

question_type: SINGLE_SELECT

why_asked:
  Determines risk_tier classification.
  Triggers regulatory_mode when a, b, or c selected.
  Controls interpretability_tier minimum floor.
  Flags protected population exposure.
  Maps to: UserIntentRecord.impact_domain
```

**Output mapping:**
```
a → impact_domain = FINANCIAL_INDIVIDUAL, risk_floor = TIER_1
b → impact_domain = HEALTH_SAFETY, risk_floor = TIER_1
c → impact_domain = LEGAL_STATUS, risk_floor = TIER_1
d → impact_domain = OPERATIONAL, risk_floor = TIER_2
e → impact_domain = ANALYTICAL, risk_floor = TIER_3
```

---

### Q4 — Explanation and Auditability Requirement
**Gate: Always issued if risk_floor IN [TIER_1, TIER_2]**
**Skip if impact_domain == ANALYTICAL**

```
question:
  "Does this model need to explain its decisions to affected individuals, regulators, or auditors?
   a) Yes — individuals must be able to understand why a decision was made about them
   b) Yes — internal auditors or regulators must be able to review decision logic
   c) Yes — both individuals and auditors require explanations
   d) No — the output is internal and no explanation is required"

question_type: SINGLE_SELECT

why_asked:
  Determines interpretability_tier.
  Controls model family eligibility gate in DataScienceRules Module 7.
  Triggers GDPR Art. 22 compliance flag when option a or c selected.
  Maps to: UserIntentRecord.explanation_requirement
```

**Output mapping:**
```
a → explanation_requirement = INDIVIDUAL_FACING, interpretability_floor = 1, gdpr_art22_flag = True
b → explanation_requirement = AUDIT_FACING, interpretability_floor = 1
c → explanation_requirement = BOTH, interpretability_floor = 1, gdpr_art22_flag = True
d → explanation_requirement = NONE, interpretability_floor = 2
```

---

### Q5 — Error Cost Asymmetry
**Gate: Issue if objective == PREDICT AND deployment_mode IN [AUTOMATED, HYBRID]**
**Skip if objective IN [SEGMENT, EXPLAIN, FORECAST]**

```
question:
  "For this model's predictions, which type of error is more costly to your organization or to affected individuals?
   a) Missing a true positive — for example, failing to detect a fraud case, defaulting borrower, or at-risk patient
   b) Producing a false alarm — for example, incorrectly flagging a good customer or healthy patient
   c) Both errors are roughly equally costly
   d) I need help quantifying this — I am not sure"

question_type: SINGLE_SELECT

why_asked:
  Determines cost_matrix structure.
  Controls threshold optimization objective in DataScienceRules Module 9.
  Triggers cost-sensitive learning flag in Module 8.
  Asymmetric responses elevate risk_tier if impact_domain == FINANCIAL or HEALTH_SAFETY.
  Maps to: UserIntentRecord.error_cost_direction
```

**Output mapping:**
```
a → error_cost_direction = FN_DOMINANT, cost_asymmetry = HIGH
b → error_cost_direction = FP_DOMINANT, cost_asymmetry = HIGH
c → error_cost_direction = SYMMETRIC, cost_asymmetry = LOW
d → error_cost_direction = UNKNOWN, cost_asymmetry = UNKNOWN
     → TRIGGER ambiguity_cost_flag = True
     → conservative fallback: treat as FN_DOMINANT if domain IN [HEALTHCARE, BANKING]
```

---

### Q6 — Fairness and Protected Population Sensitivity
**Gate: Issue if EITHER:**
- `DatasetIdentity.protected_attribute_flag == True`
- `impact_domain IN [FINANCIAL_INDIVIDUAL, HEALTH_SAFETY, LEGAL_STATUS]`
- `DatasetIdentity.domain IN [BANKING, HEALTHCARE, INSURANCE]`

**Skip if impact_domain == ANALYTICAL AND domain == GENERAL AND protected_attribute_flag == False**

```
question:
  "Does this model make decisions that could affect people differently based on characteristics such as age, gender, race, disability, or geography?
   a) Yes — and we are required to monitor and report on fairness outcomes
   b) Yes — we want to monitor fairness but have no formal reporting requirement
   c) Possibly — we have not assessed this yet
   d) No — this model does not affect individuals or does not use any such characteristics"

question_type: SINGLE_SELECT

why_asked:
  Determines fairness_sensitivity flag.
  Controls disparate impact testing requirement in DataScienceRules Module 13 equivalent.
  Elevates regulatory_mode when option a selected.
  Triggers protected_attribute_blocking gate in Module 2.
  Maps to: UserIntentRecord.fairness_sensitivity
```

**Output mapping:**
```
a → fairness_sensitivity = HIGH, fairness_reporting_required = True, regulatory_mode_floor = REGULATED
b → fairness_sensitivity = MODERATE, fairness_reporting_required = False
c → fairness_sensitivity = MODERATE, fairness_reporting_required = False
    → conservative fallback: treat as b
d → fairness_sensitivity = LOW, fairness_reporting_required = False
```

---

### Q7 — Regulatory and Compliance Exposure
**Gate: Issue if EITHER:**
- `DatasetIdentity.regulatory_exposure_flag == True`
- `impact_domain IN [FINANCIAL_INDIVIDUAL, HEALTH_SAFETY, LEGAL_STATUS]`
- `fairness_sensitivity IN [HIGH, MODERATE]`

**Skip if impact_domain == ANALYTICAL AND regulatory_exposure_flag == False**

```
question:
  "Is this model subject to any regulatory, legal, or compliance requirements?
   a) Yes — it must comply with financial services regulation (e.g., model risk management requirements)
   b) Yes — it must comply with data protection or privacy law (e.g., GDPR or equivalent)
   c) Yes — it must comply with sector-specific clinical or safety regulation
   d) Yes — multiple regulatory frameworks apply
   e) Not formally, but internal governance standards apply
   f) No regulatory requirements apply to this model"

question_type: MULTI_SELECT

why_asked:
  Determines regulatory_mode enum.
  Controls IMV separation requirement.
  Controls approval workflow tier.
  Controls audit log retention period.
  Maps to: UserIntentRecord.regulatory_exposure
```

**Output mapping:**
```
a → regulatory_frameworks = [SR_11_7], regulatory_mode = REGULATED
b → regulatory_frameworks = [GDPR], regulatory_mode = GDPR_STRICT
c → regulatory_frameworks = [SECTOR_CLINICAL], regulatory_mode = REGULATED
d → regulatory_frameworks = [MULTI], regulatory_mode = REGULATED (strictest applicable)
e → regulatory_frameworks = [INTERNAL], regulatory_mode = STANDARD
f → regulatory_frameworks = [], regulatory_mode = STANDARD
a + b → regulatory_mode = GDPR_STRICT (GDPR_STRICT supersedes REGULATED)
```

---

### Q8 — Time Awareness and Decision Horizon
**Gate: Issue if EITHER:**
- `DatasetIdentity.has_temporal_column == True`
- `DatasetIdentity.dataset_type IN [TIME_SERIES, PANEL]`
- `objective == FORECAST`

**Skip if dataset_type == TABULAR AND has_temporal_column == False AND objective != FORECAST**

```
question:
  "Does the timing of data matter for this model — for example, does the model need to predict future outcomes, use only information available at a specific past date, or track how things change over time?
   a) Yes — the model predicts future values using historical sequences
   b) Yes — the model must only use data available at the time each decision was made, not information that came later
   c) Yes — we need to understand how outcomes or patterns change across time periods
   d) No — time ordering is not relevant to this analysis"

question_type: SINGLE_SELECT

why_asked:
  Determines time_awareness_required flag.
  Triggers temporal split enforcement in DataScienceRules Module 6.
  Triggers temporal leakage detection in Module 2.
  Controls rolling window CV vs standard CV routing.
  Maps to: UserIntentRecord.time_awareness
```

**Output mapping:**
```
a → time_awareness = FORECAST, temporal_split_required = True, gap_injection = True
b → time_awareness = POINT_IN_TIME_STRICT, temporal_split_required = True, gap_injection = True
c → time_awareness = TREND_ANALYSIS, temporal_split_required = True
d → time_awareness = NONE, temporal_split_required = False
```

---

## Conditional Blocks Summary

```
ALWAYS ISSUE:           Q1
IF objective IN [PREDICT, FORECAST, ANOMALY_DETECT]: Q2
IF deployment_mode IN [AUTOMATED, HYBRID]: Q3
IF risk_floor IN [TIER_1, TIER_2]: Q4
IF objective == PREDICT AND deployment_mode IN [AUTOMATED, HYBRID]: Q5
IF protected_attribute_flag OR impact_domain is individual-facing: Q6
IF regulatory_exposure_flag OR impact_domain is individual-facing: Q7
IF has_temporal_column OR dataset_type is temporal OR objective == FORECAST: Q8
```

---

## Ambiguity Detection and Escalation

```python
# After all questions completed, run ambiguity resolution pass

ambiguity_conditions = {
    "cost_matrix_unknown": error_cost_direction == UNKNOWN,
    "risk_tier_indeterminate": impact_domain == UNKNOWN AND deployment_mode == AUTOMATED,
    "domain_conflict": user_stated_domain != DatasetIdentity.domain AND both are not UNKNOWN,
    "regulatory_underspecified": deployment_mode == AUTOMATED AND regulatory_exposure == NONE AND domain IN [BANKING, HEALTHCARE]
}

FOR each condition in ambiguity_conditions:
    IF condition == True:
        SET ambiguity_flag[condition] = True
        PASS flag to IntentInferenceRules for conservative mapping

IF ambiguity_flag.risk_tier_indeterminate == True:
    APPLY conservative escalation:
    SET risk_tier = TIER_1 pending IntentInference resolution

IF ambiguity_flag.regulatory_underspecified == True AND domain IN [BANKING, HEALTHCARE]:
    APPLY conservative escalation:
    SET regulatory_mode = REGULATED pending IntentInference resolution
    LOG warning: "Domain implies regulatory exposure. Conservative regulatory mode applied."
```

---

## Conservative Fallback Behavior

```
IF any required question was skipped due to incorrect gate evaluation:
    SET all downstream fields derived from skipped question = CONSERVATIVE_DEFAULT

CONSERVATIVE_DEFAULTS:
    risk_tier = TIER_1
    interpretability_tier = 1
    regulatory_mode = REGULATED
    deployment_mode = HUMAN_REVIEWED
    fairness_sensitivity = HIGH
    time_awareness = NONE
    cost_asymmetry = SYMMETRIC
```

---

## Output Contract

QuestionBuilder produces a raw answer record passed directly to IntentInferenceRules:

```
RawAnswerRecord:
  session_id:               UUID
  dataset_identity_ref:     DatasetIdentity.id from GAL
  questions_issued:         [Q1, Q2, ...] list of issued question IDs
  answers:                  {Q1: selected_option, Q2: selected_option, ...}
  ambiguity_flags:          {flag_name: Boolean}
  conservative_fallbacks_applied: [list of field names where fallback used]
  timestamp:                ISO timestamp
```
