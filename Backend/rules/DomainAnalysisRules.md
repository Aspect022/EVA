# DomainAnalysisRules.md
## Enterprise Domain Analysis and Dataset Identity Engine — Backend Governance Specification

**Version:** 3.0
**Status:** ENTERPRISE — Deterministic Governance Engine
**Produces:** `DatasetIdentity` object → written to GAL
**Consumed by:** QuestionBuilderRules, IntentInferenceRules, DRIL, EPR, DataScienceRules engine

---

## SECTION 0 — Governance Preamble

1. This file is a **deterministic governance specification**. All output values are produced by fixed rule logic. No probabilistic or advisory override is permitted.
2. **RAG is advisory only.** RAG context may inform upstream prompt construction but must NEVER override any field produced by this engine.
3. Once `DatasetIdentity` is written to GAL, it is **immutable** for the lifecycle of that session. No downstream module may modify it.
4. This engine performs **classification and inference only**. No data cleaning, transformation, or imputation occurs here.
5. All output enum values must exactly match values declared in `SECTION 1 — Enum Registry` below. No other values are permitted.
6. Any field that cannot be resolved by deterministic logic must receive the corresponding `UNKNOWN` or conservative fallback value declared in `SECTION 5`.

---

## SECTION 1 — Enum Registry

All enum values produced by this engine. Sourced from `DataScienceRules.md §Global Constants`. No values outside this registry may appear in any output field.

| Field | Legal Values |
|---|---|
| `domain` | `BANKING` \| `HEALTHCARE` \| `INSURANCE` \| `GENERAL` \| `UNKNOWN` |
| `domain_confidence` | `HIGH` \| `MEDIUM` \| `LOW` |
| `dataset_type` | `TABULAR` \| `TIME_SERIES` \| `PANEL` \| `NLP` \| `CV` \| `GRAPH` \| `UNKNOWN` |
| `dataset_type_confidence` | `HIGH` \| `MEDIUM` \| `LOW` |
| `label_type` | `BINARY` \| `MULTICLASS` \| `REGRESSION` \| `NONE` \| `UNKNOWN` |
| `domain_risk_flag` | `LOW` \| `MODERATE` \| `HIGH` \| `CRITICAL` |
| `domain_conflict_flag` | `Boolean` |
| `has_target_column` | `Boolean` |
| `has_temporal_column` | `Boolean` |
| `has_group_column` | `Boolean` |
| `has_pii_detected` | `Boolean` |
| `protected_attribute_flag` | `Boolean` |
| `regulatory_exposure_flag` | `Boolean` |
| `high_risk_target_flag` | `Boolean` |
| `escalation_triggers` | List of codes from `SECTION 6 — Escalation Registry` |

---

## SECTION 2 — Input Contract

```
RawDatasetProfile:
  column_names:             [list of strings]
  column_dtypes:            {column_name: dtype_string}
  column_sample_values:     {column_name: [up to 5 sample values, anonymized]}
  column_missing_pcts:      {column_name: float 0.0–1.0}
  n_rows:                   Integer
  n_columns:                Integer
  file_name:                String or NULL
  user_stated_domain:       String or NULL (free text, may be empty)
  user_stated_objective:    String or NULL (free text, may be empty)
  ingest_timestamp:         ISO timestamp
```

---

## SECTION 3 — Governance Precedence Hierarchy

The following precedence stack is enforced at every decision point in this engine. A higher-priority outcome always supersedes a lower one.

```
Level 1 (Highest): HARD_STOP
  → Pipeline terminates. DatasetIdentity is NOT written to GAL.
  → Trigger: critical structural ambiguity (DATASET_TYPE_CANNOT_BE_INFERRED)
    or PII_DETECTED requiring governance clearance before any downstream processing.

Level 2: Escalation Trigger
  → DatasetIdentity is written to GAL WITH the escalation code in escalation_triggers[].
  → Downstream modules must check escalation_triggers before processing.

Level 3: Conservative Fallback
  → Applied when inference is ambiguous and no HARD_STOP condition is met.
  → Fallback value is written; conservative_override is logged.
  → See SECTION 5 for all fallback values.

Level 4 (Lowest): Inferred Value
  → Normal deterministic classification output.
  → Applied only when Levels 1–3 do not apply.
```

> No output field may be `NULL` for a governed field. If Level 4 cannot resolve a value, Level 3 must apply.

---

## SECTION 4 — Module Blocks

### BLOCK 1 — Dataset Type Classification

```python
# STEP 1: Temporal signal detection
temporal_keyword_patterns = [
    "date", "time", "timestamp", "datetime", "period", "month", "year",
    "week", "quarter", "day", "hour", "minute", "epoch", "created_at",
    "updated_at", "event_date", "observation_date", "report_date"
]

temporal_dtype_patterns = ["datetime", "date", "timestamp", "int64_epoch"]

temporal_column_candidates = []
FOR each column in column_names:
    IF any(pattern in column.lower() for pattern in temporal_keyword_patterns):
        temporal_column_candidates.append(column)
    IF column_dtypes[column] in temporal_dtype_patterns:
        IF column NOT IN temporal_column_candidates:
            temporal_column_candidates.append(column)

IF temporal_column_candidates.count > 0:
    has_temporal_column = True
    IF temporal_column_candidates.count == 1:
        temporal_column_name = temporal_column_candidates[0]
    ELSE:
        temporal_column_name = argmax(n_distinct_values, over=temporal_column_candidates)
ELSE:
    has_temporal_column = False
    temporal_column_name = NULL

# STEP 2: Group signal detection
group_keyword_patterns = [
    "id", "customer_id", "patient_id", "account_id", "entity_id",
    "user_id", "loan_id", "policy_id", "subject_id", "member_id",
    "company_id", "firm_id", "borrower_id"
]

group_column_candidates = []
FOR each column in column_names:
    IF any(pattern in column.lower() for pattern in group_keyword_patterns):
        IF column_dtypes[column] in ["int64", "object", "string"]:
            group_column_candidates.append(column)

IF group_column_candidates.count > 0:
    has_group_column = True
    group_column_name = group_column_candidates[0]
ELSE:
    has_group_column = False
    group_column_name = NULL

# STEP 3: Dataset type classification (deterministic routing)
IF has_temporal_column == True AND has_group_column == True:
    dataset_type = PANEL
    dataset_type_confidence = HIGH

ELIF has_temporal_column == True AND has_group_column == False:
    dataset_type = TIME_SERIES
    dataset_type_confidence = MEDIUM
    # SOFT_WARN: group column may be present but not named predictably
    escalation_triggers.append("TIME_SERIES_PANEL_AMBIGUITY_NO_GROUP_COLUMN")

ELIF all(dtype in ["float64", "int64", "bool", "category", "object"] for dtype in column_dtypes.values()):
    dataset_type = TABULAR
    dataset_type_confidence = HIGH

ELIF any(
    column_dtypes[column] in ["object", "string"]
    AND mean(len(str(v)) for v in column_sample_values[column]) > 50
    for column in column_names
):
    dataset_type = NLP
    dataset_type_confidence = MEDIUM

ELIF n_columns > 1000 AND all(dtype in ["float64", "int64"] for dtype in column_dtypes.values()):
    dataset_type = CV
    dataset_type_confidence = LOW
    escalation_triggers.append("HIGH_DIMENSIONAL_NUMERIC_AMBIGUOUS_CV_OR_TABULAR")

ELSE:
    dataset_type = UNKNOWN
    dataset_type_confidence = LOW
    escalation_triggers.append("DATASET_TYPE_CANNOT_BE_INFERRED")
    # SECTION 3 Level 1: This escalation code triggers HARD_STOP in SECTION 6.
```

---

### BLOCK 2 — Target Column and Label Type Inference

```python
# STEP 1: Target column candidate detection
target_keyword_patterns = [
    "target", "label", "outcome", "y", "flag", "default", "churn",
    "fraud", "survived", "death", "readmission", "claim", "loss",
    "default_flag", "is_fraud", "is_churn", "event", "response",
    "conversion", "approved", "rejected", "positive", "negative",
    "diagnosis", "mortality", "prediction"
]

target_candidates = []
FOR each column in column_names:
    IF any(pattern in column.lower() for pattern in target_keyword_patterns):
        target_candidates.append(column)

# STEP 2: Label type inference
IF target_candidates.count > 0:
    has_target_column = True
    primary_candidate = target_candidates[0]
    inferred_target_column = primary_candidate

    target_sample = column_sample_values[primary_candidate]
    target_dtype = column_dtypes[primary_candidate]
    n_distinct = len(set(target_sample))

    IF target_dtype in ["bool"] OR set(target_sample).issubset(
        {0, 1, "0", "1", "True", "False", "true", "false", "yes", "no", "Y", "N"}
    ):
        label_type = BINARY

    ELIF target_dtype in ["float64"] AND n_distinct > 10:
        label_type = REGRESSION

    ELIF target_dtype in ["int64", "object", "category"] AND n_distinct <= 20 AND n_distinct > 2:
        label_type = MULTICLASS

    ELIF target_dtype in ["int64"] AND n_distinct == 2:
        label_type = BINARY

    ELSE:
        label_type = UNKNOWN

ELSE:
    has_target_column = False
    inferred_target_column = NULL
    label_type = NONE
```

---

### BLOCK 3 — Domain Classification

```python
# STEP 1: Column-name-based domain signal scoring
domain_signals = {
    BANKING: 0,
    HEALTHCARE: 0,
    INSURANCE: 0,
    GENERAL: 0
}

BANKING_KEYWORDS = [
    "credit", "loan", "default", "pd", "lgd", "ead", "fico", "score",
    "balance", "delinquent", "repayment", "mortgage", "debt", "interest_rate",
    "ltv", "collateral", "covenant", "exposure", "npl", "ecl", "provision",
    "account", "transaction", "payment", "overdraft", "bureau", "income",
    "dti", "revolving", "installment", "origination"
]

HEALTHCARE_KEYWORDS = [
    "patient", "diagnosis", "icd", "cpt", "procedure", "medication",
    "lab", "vitals", "bmi", "age", "comorbidity", "readmission", "los",
    "mortality", "sepsis", "icu", "emergency", "clinical", "symptom",
    "discharge", "admission", "physician", "hospital", "drug", "dose",
    "blood", "heart", "diabetes", "cancer", "chronic"
]

INSURANCE_KEYWORDS = [
    "policy", "premium", "claim", "insured", "coverage", "deductible",
    "underwrite", "risk_score", "exposure_value", "loss_ratio",
    "reinsurance", "actuarial", "lapse", "renewal", "endorsement",
    "catastrophe", "nat_cat", "severity", "frequency", "reserve"
]

FOR each column in column_names:
    col_lower = column.lower()
    FOR keyword in BANKING_KEYWORDS:
        IF keyword in col_lower:
            domain_signals[BANKING] += 1
    FOR keyword in HEALTHCARE_KEYWORDS:
        IF keyword in col_lower:
            domain_signals[HEALTHCARE] += 1
    FOR keyword in INSURANCE_KEYWORDS:
        IF keyword in col_lower:
            domain_signals[INSURANCE] += 1

# STEP 2: User-stated domain parsing
user_domain_map = {
    "bank": BANKING, "banking": BANKING, "financial": BANKING, "credit": BANKING,
    "lending": BANKING, "fintech": BANKING, "fund": BANKING,
    "health": HEALTHCARE, "healthcare": HEALTHCARE, "clinical": HEALTHCARE,
    "hospital": HEALTHCARE, "medical": HEALTHCARE, "pharma": HEALTHCARE,
    "insurance": INSURANCE, "insur": INSURANCE, "underwriting": INSURANCE,
    "actuarial": INSURANCE
}

user_stated_domain_parsed = NULL
IF user_stated_domain IS NOT NULL:
    FOR phrase, mapped_domain in user_domain_map.items():
        IF phrase in user_stated_domain.lower():
            user_stated_domain_parsed = mapped_domain
            domain_signals[mapped_domain] += 5  # User statement is a strong governance signal

# STEP 3: Domain assignment (deterministic)
max_signal = max(domain_signals.values())
winning_domain = argmax(domain_signals)

IF max_signal == 0:
    domain = GENERAL
    domain_confidence = MEDIUM

ELIF max_signal >= 5:
    domain = winning_domain
    domain_confidence = HIGH

ELIF max_signal >= 2:
    domain = winning_domain
    domain_confidence = MEDIUM

ELSE:
    domain = GENERAL
    domain_confidence = LOW

# STEP 4: Conflict detection and governance resolution
# Governance rule: user-stated domain overrides inferred domain ONLY when max_signal < 5.
# When max_signal >= 5, a conflict is escalated — it does NOT silently resolve.

IF user_stated_domain_parsed IS NOT NULL AND user_stated_domain_parsed != domain:
    IF max_signal < 5:
        # User statement takes precedence over weak signal
        domain = user_stated_domain_parsed
        domain_conflict_flag = True
        escalation_triggers.append("DOMAIN_SIGNAL_CONFLICT_USER_VS_INFERRED")
    ELSE:
        # Strong inferred signal conflicts with user statement — escalate, do not override
        domain_conflict_flag = True
        escalation_triggers.append("DOMAIN_CONFLICT_HIGH_SIGNAL_USER_MISMATCH")
        # domain remains as winning_domain (inferred); conflict surfaced for human resolution
ELSE:
    domain_conflict_flag = False
```

---

### BLOCK 4 — PII and Protected Attribute Detection

```python
PII_KEYWORD_PATTERNS = [
    "name", "first_name", "last_name", "surname", "full_name",
    "email", "phone", "mobile", "address", "zip", "postcode",
    "ssn", "social_security", "national_id", "passport", "dob",
    "date_of_birth", "ip_address", "device_id", "cookie"
]

PROTECTED_ATTRIBUTE_PATTERNS = [
    "age", "gender", "sex", "race", "ethnicity", "nationality",
    "religion", "disability", "marital_status", "pregnancy",
    "sexual_orientation", "political", "union_membership",
    "region", "zip", "postcode", "country"
]

pii_column_candidates = []
protected_attribute_candidates = []

FOR each column in column_names:
    col_lower = column.lower()

    IF any(pattern in col_lower for pattern in PII_KEYWORD_PATTERNS):
        pii_column_candidates.append(column)

    IF any(pattern in col_lower for pattern in PROTECTED_ATTRIBUTE_PATTERNS):
        protected_attribute_candidates.append(column)

has_pii_detected = pii_column_candidates.count > 0
protected_attribute_flag = protected_attribute_candidates.count > 0

IF has_pii_detected == True:
    escalation_triggers.append("PII_DETECTED_VERIFY_ACCESS_CONTROLS")
```

---

### BLOCK 5 — High-Risk Target Registry and Domain Risk Flag Assignment

```
RISK_TARGET_REGISTRY:

  BANKING:
    - "default", "pd", "probability_of_default", "default_flag"
    - "credit_decision", "loan_approved", "fraud", "is_fraud"
    - "aml_flag", "sanction_flag"

  HEALTHCARE:
    - "mortality", "death", "readmission", "adverse_event"
    - "sepsis", "icu_admission", "diagnosis", "cancer", "survival"

  INSURANCE:
    - "claim", "large_claim", "fraud_claim", "lapse", "loss"
```

```python
# High-risk target detection (uses RISK_TARGET_REGISTRY above)
high_risk_target_flag = False
high_risk_target_name = NULL

IF has_target_column == True AND inferred_target_column IS NOT NULL:
    col_lower = inferred_target_column.lower()
    IF domain IN RISK_TARGET_REGISTRY:
        FOR target_pattern in RISK_TARGET_REGISTRY[domain]:
            IF target_pattern in col_lower:
                high_risk_target_flag = True
                high_risk_target_name = inferred_target_column

# Domain risk flag matrix (deterministic)
IF domain == BANKING:
    IF high_risk_target_flag == True:
        domain_risk_flag = CRITICAL
    ELIF has_pii_detected == True OR protected_attribute_flag == True:
        domain_risk_flag = HIGH
    ELSE:
        domain_risk_flag = MODERATE

ELIF domain == HEALTHCARE:
    IF high_risk_target_flag == True:
        domain_risk_flag = CRITICAL
    ELSE:
        domain_risk_flag = HIGH
    # Healthcare is never LOW or MODERATE regardless of target

ELIF domain == INSURANCE:
    IF high_risk_target_flag == True:
        domain_risk_flag = HIGH
    ELIF protected_attribute_flag == True:
        domain_risk_flag = HIGH
    ELSE:
        domain_risk_flag = MODERATE

ELSE:  # GENERAL
    IF protected_attribute_flag == True AND label_type in [BINARY, MULTICLASS]:
        domain_risk_flag = MODERATE
    ELSE:
        domain_risk_flag = LOW

# Regulatory exposure flag
IF domain in [BANKING, HEALTHCARE, INSURANCE]:
    regulatory_exposure_flag = True
ELIF protected_attribute_flag == True AND label_type != NONE:
    regulatory_exposure_flag = True
ELIF has_pii_detected == True AND label_type in [BINARY, MULTICLASS]:
    regulatory_exposure_flag = True
ELSE:
    regulatory_exposure_flag = False
```

---

### BLOCK 6 — Domain Feature Registry Reference

```
domain_feature_registry_ref assignment:

IF domain == BANKING:
    domain_feature_registry_ref = "registry://banking/v2"

    BANKING REGISTRY — CONCEPTUAL STRUCTURE:

    regulatory_capital_features:
      # No imputation without MRM approval
      - pd_score, lgd_estimate, ead_value, exposure_at_default,
        collateral_value, risk_weight, ecl_provision

    high_sensitivity_features:
      # Proxy for creditworthiness — require leakage review
      - bureau_score, internal_score, delinquency_count, days_past_due,
        utilization_rate, credit_limit, revolving_balance

    prohibited_for_credit_decisions:
      # Source: ECOA, Fair Credit Reporting Act, national equivalents
      - race, ethnicity, gender, age (unless legally permitted), religion,
        national_origin, marital_status, zip_code (if proxy for race)

ELIF domain == HEALTHCARE:
    domain_feature_registry_ref = "registry://healthcare/v2"

    HEALTHCARE REGISTRY — CONCEPTUAL STRUCTURE:

    clinical_features:
      # Missing values clinically significant — Module 3 hard stop applies
      - lab_results, vitals, medications, procedures, diagnoses

    high_sensitivity_features:
      # PHI under HIPAA — access restricted
      - patient_id, date_of_birth, address, mrn, ssn, device_identifiers

    high_risk_outcome_features:
      # FN cost floor = 10x FP cost unless overridden in Business Decision Charter
      - mortality, adverse_event, sepsis_flag, icu_admission, readmission_30d

ELIF domain == INSURANCE:
    domain_feature_registry_ref = "registry://insurance/v2"

    INSURANCE REGISTRY — CONCEPTUAL STRUCTURE:

    actuarial_reserve_features:
      # Cannot be imputed without actuarial sign-off
      - incurred_loss, reported_claims, reserve_estimate, ibnr

    prohibited_underwriting_features:
      # Jurisdiction-dependent — flag for legal review
      - genetic_data, disability_status (some jurisdictions)

ELSE:
    domain_feature_registry_ref = "registry://general/v1"
```

---

### BLOCK 7 — Protected Attribute Registry by Domain

```
PROTECTED_ATTRIBUTES_BY_DOMAIN:

  BANKING:
    legally_protected:
      - race, color, religion, national_origin, sex,
        marital_status, age, familial_status, disability
    proxy_risk_high:
      - zip_code, postal_code, neighborhood, surname,
        first_name, language_preference
    regulatory_source: [ECOA, FHA, FCRA, national equivalents]

  HEALTHCARE:
    legally_protected:
      - race, color, national_origin, sex, age, disability, religion
    proxy_risk_high:
      - zip_code, insurance_type, language, socioeconomic_indicator
    regulatory_source: [Section 1557 ACA, HIPAA, national equivalents]

  INSURANCE:
    legally_protected:
      - race, color, religion, national_origin, sex,
        marital_status, age, disability
    proxy_risk_high:
      - zip_code, credit_score (in some jurisdictions), occupation
    regulatory_source: [State insurance codes, national equivalents]

  GENERAL:
    legally_protected:
      - race, gender, age, disability, religion,
        national_origin, pregnancy
    proxy_risk_high:
      - zip_code, name, language
    regulatory_source: [GDPR Article 9, national equivalents]
```

---

### BLOCK 8 — Regulatory Defaults by Domain

```
REGULATORY_DEFAULTS:

  BANKING:
    regulatory_mode_default:       REGULATED
    regulatory_frameworks:         [SR_11_7]
    imv_separation_required:       True
    approval_expiry_tier1_days:    180
    approval_expiry_tier2_days:    365
    audit_log_retention_years:     7
    fairness_di_threshold:         0.80
    model_inventory_required:      True
    challenger_framework_required: True

  HEALTHCARE:
    regulatory_mode_default:       REGULATED
    regulatory_frameworks:         [SECTOR_CLINICAL]
    imv_separation_required:       True
    approval_expiry_tier1_days:    180
    approval_expiry_tier2_days:    365
    audit_log_retention_years:     10
    fairness_di_threshold:         0.80
    minimum_recall_floor:          0.85
    model_inventory_required:      True
    challenger_framework_required: False

  INSURANCE:
    regulatory_mode_default:       REGULATED
    regulatory_frameworks:         [SECTOR_CLINICAL]
    imv_separation_required:       True
    approval_expiry_tier1_days:    365
    approval_expiry_tier2_days:    365
    audit_log_retention_years:     7
    fairness_di_threshold:         0.80
    model_inventory_required:      True
    challenger_framework_required: True

  GENERAL:
    regulatory_mode_default:       STANDARD
    regulatory_frameworks:         [NONE]
    imv_separation_required:       False
    approval_expiry_tier1_days:    365
    approval_expiry_tier2_days:    730
    audit_log_retention_years:     3
    fairness_di_threshold:         0.80
    model_inventory_required:      False
    challenger_framework_required: False
```

```python
# Apply regulatory defaults to DatasetIdentity for downstream module consumption
DatasetIdentity.regulatory_defaults = REGULATORY_DEFAULTS[domain]
```

---

### BLOCK 9 — Domain-Specific Escalation Trigger Evaluation

```python
# Run after all blocks complete.
# All triggered codes are appended to escalation_triggers[].
# Escalation triggers do NOT halt this engine's output — they are
# carried in DatasetIdentity and evaluated by downstream modules.
# Exception: DATASET_TYPE_CANNOT_BE_INFERRED triggers HARD_STOP per SECTION 6.

ESCALATION_RULES = [
    {
        "code": "HEALTHCARE_ANY_TARGET",
        "condition": domain == HEALTHCARE AND has_target_column == True,
        "reason": "All supervised models in healthcare require clinical SME review before processing.",
        "action": "NOTIFY_CLINICAL_SME_BEFORE_PROCEEDING"
    },
    {
        "code": "BANKING_CREDIT_DECISION_TARGET",
        "condition": domain == BANKING AND high_risk_target_flag == True AND label_type == BINARY,
        "reason": "Credit decision model detected. SR 11-7 independent validation required.",
        "action": "REQUIRE_IMV_ASSIGNMENT_BEFORE_TRAINING"
    },
    {
        "code": "PII_DETECTED_VERIFY_ACCESS_CONTROLS",
        "condition": has_pii_detected == True,
        "reason": "PII columns detected. Access controls and GDPR processing basis must be verified.",
        "action": "HALT_UNTIL_DATA_GOVERNANCE_CLEARED"
    },
    {
        "code": "DATASET_TYPE_CANNOT_BE_INFERRED",
        "condition": dataset_type == UNKNOWN,
        "reason": "Dataset structure cannot be inferred. Human review required before classification.",
        "action": "HALT_PENDING_STRUCTURE_CLARIFICATION"
    },
    {
        "code": "HIGH_DIMENSIONAL_AMBIGUOUS",
        "condition": n_columns > 1000 AND dataset_type_confidence == LOW,
        "reason": "Dataset has >1000 features with ambiguous type. CV or embedding structure possible.",
        "action": "ESCALATE_TO_ML_ENGINEERING_FOR_STRUCTURE_REVIEW"
    },
    {
        "code": "DOMAIN_SIGNAL_CONFLICT_USER_VS_INFERRED",
        "condition": domain_conflict_flag == True AND max_signal < 5,
        "reason": "User-stated domain conflicts with inferred domain under low signal. User statement applied.",
        "action": "RESOLVE_DOMAIN_BEFORE_DOWNSTREAM_PROCESSING"
    },
    {
        "code": "DOMAIN_CONFLICT_HIGH_SIGNAL_USER_MISMATCH",
        "condition": domain_conflict_flag == True AND max_signal >= 5,
        "reason": "Strong inferred domain signal conflicts with user statement. Inferred domain retained. Human resolution required.",
        "action": "ESCALATE_TO_DOMAIN_OWNER_FOR_RESOLUTION"
    },
    {
        "code": "PROTECTED_ATTRIBUTES_IN_BANKING_CREDIT",
        "condition": domain == BANKING AND high_risk_target_flag == True AND protected_attribute_flag == True,
        "reason": "Protected attributes detected in banking credit model dataset. ECOA compliance assessment required.",
        "action": "NOTIFY_COMPLIANCE_BEFORE_FEATURE_ENGINEERING"
    },
    {
        "code": "HEALTHCARE_MORTALITY_TARGET",
        "condition": domain == HEALTHCARE AND high_risk_target_name IS NOT NULL
                     AND any(["mortality", "death", "sepsis"] in high_risk_target_name.lower()),
        "reason": "Life-critical outcome target detected. FN cost floor and minimum recall floor apply.",
        "action": "REQUIRE_CLINICAL_SME_AND_ETHICS_REVIEW"
    },
    {
        "code": "TIME_SERIES_PANEL_AMBIGUITY_NO_GROUP_COLUMN",
        "condition": dataset_type == TIME_SERIES AND has_group_column == False,
        "reason": "TIME_SERIES classification — group column not detected. Dataset may be PANEL with unpredictably named group column.",
        "action": "REVIEW_DATASET_STRUCTURE_FOR_PANEL_CLASSIFICATION"
    }
]

FOR each rule in ESCALATION_RULES:
    IF rule.condition == True:
        IF rule.code NOT IN escalation_triggers:
            escalation_triggers.append(rule.code)
```

---

## SECTION 5 — Conservative Fallback Table

Applied when deterministic inference cannot resolve a governed field (Level 3 of the Governance Precedence Hierarchy). All fallback values are enums from `SECTION 1`.

| Field | Conservative Fallback Value | Trigger Condition |
|---|---|---|
| `domain` | `GENERAL` | No domain signal detected (max_signal == 0) |
| `domain_confidence` | `LOW` | max_signal in [1] only |
| `dataset_type` | `TABULAR` | No temporal or structural signals, mixed dtypes |
| `dataset_type_confidence` | `LOW` | dataset_type resolved by elimination |
| `label_type` | `UNKNOWN` | Target column detected but dtype/distinct count ambiguous |
| `domain_risk_flag` | `MODERATE` | domain == GENERAL with some PII or protected attributes |
| `regulatory_exposure_flag` | `True` | domain is GENERAL but has PII + supervised task |
| `high_risk_target_flag` | `False` | Target column absent or domain not in RISK_TARGET_REGISTRY |
| `has_pii_detected` | `False` | No PII keyword patterns matched |
| `protected_attribute_flag` | `False` | No protected attribute patterns matched |

---

## SECTION 6 — Escalation Registry

All escalation codes produced by this engine. Downstream modules must check `DatasetIdentity.escalation_triggers` before executing their own logic.

| CODE | SEVERITY | ACTION | SLA | DOWNSTREAM EFFECT |
|---|---|---|---|---|
| `DATASET_TYPE_CANNOT_BE_INFERRED` | HARD_STOP | HALT_PENDING_STRUCTURE_CLARIFICATION | Immediate | DatasetIdentity NOT written to GAL. Pipeline halted. |
| `PII_DETECTED_VERIFY_ACCESS_CONTROLS` | SOFT_WARN | HALT_UNTIL_DATA_GOVERNANCE_CLEARED | 24h | Downstream modules must gate on governance clearance |
| `HEALTHCARE_ANY_TARGET` | SOFT_WARN | NOTIFY_CLINICAL_SME_BEFORE_PROCEEDING | 5 business days | QBII and DRIL must await SME confirmation |
| `BANKING_CREDIT_DECISION_TARGET` | SOFT_WARN | REQUIRE_IMV_ASSIGNMENT_BEFORE_TRAINING | 48h | EPR and DataScienceRules must await IMV assignment |
| `HIGH_DIMENSIONAL_AMBIGUOUS` | SOFT_WARN | ESCALATE_TO_ML_ENGINEERING_FOR_STRUCTURE_REVIEW | 48h | dataset_type_confidence = LOW propagates to downstream |
| `DOMAIN_SIGNAL_CONFLICT_USER_VS_INFERRED` | SOFT_WARN | RESOLVE_DOMAIN_BEFORE_DOWNSTREAM_PROCESSING | 24h | domain_conflict_flag = True propagates |
| `DOMAIN_CONFLICT_HIGH_SIGNAL_USER_MISMATCH` | SOFT_WARN | ESCALATE_TO_DOMAIN_OWNER_FOR_RESOLUTION | 24h | Inferred domain retained; conflict logged for audit |
| `PROTECTED_ATTRIBUTES_IN_BANKING_CREDIT` | SOFT_WARN | NOTIFY_COMPLIANCE_BEFORE_FEATURE_ENGINEERING | 24h | Module 2 proxy detection must run with full flag list |
| `HEALTHCARE_MORTALITY_TARGET` | SOFT_WARN | REQUIRE_CLINICAL_SME_AND_ETHICS_REVIEW | 5 business days | FN cost floor enforced in DataScienceRules Module 9 |
| `TIME_SERIES_PANEL_AMBIGUITY_NO_GROUP_COLUMN` | SOFT_WARN | REVIEW_DATASET_STRUCTURE_FOR_PANEL_CLASSIFICATION | 48h | dataset_type_confidence = MEDIUM; downstream routing may need correction |

---

## SECTION 7 — Validation Rules

Run after all blocks complete, before `DatasetIdentity` is assembled and written to GAL.

```python
# V1: domain must be a legal enum value
ASSERT domain IN [BANKING, HEALTHCARE, INSURANCE, GENERAL, UNKNOWN]

# V2: dataset_type must be a legal enum value
ASSERT dataset_type IN [TABULAR, TIME_SERIES, PANEL, NLP, CV, GRAPH, UNKNOWN]

# V3: label_type must be a legal enum value
ASSERT label_type IN [BINARY, MULTICLASS, REGRESSION, NONE, UNKNOWN]

# V4: domain_risk_flag must be a legal enum value
ASSERT domain_risk_flag IN [LOW, MODERATE, HIGH, CRITICAL]

# V5: HARD_STOP if dataset_type == UNKNOWN (never write ambiguous type to GAL)
IF dataset_type == UNKNOWN:
    RETURN HARD_STOP
    reason = "dataset_type == UNKNOWN. DatasetIdentity will not be written to GAL."

# V6: has_target_column and inferred_target_column consistency
IF has_target_column == True AND inferred_target_column IS NULL:
    inferred_target_column = target_candidates[0]  # recover with first candidate

IF has_target_column == False:
    inferred_target_column = NULL
    label_type = NONE

# V7: domain_risk_flag floor for regulated domains
IF domain IN [BANKING, HEALTHCARE, INSURANCE]:
    IF domain_risk_flag == LOW:
        domain_risk_flag = MODERATE
        # Regulated domains cannot have LOW risk floor

# V8: regulatory_exposure_flag is always True for regulated domains
IF domain IN [BANKING, HEALTHCARE, INSURANCE]:
    regulatory_exposure_flag = True
```

---

## SECTION 8 — Output Contract

`DatasetIdentity` object produced by this engine:

```
DatasetIdentity:
  identity_id:                    UUID (immutable)
  raw_profile_ref:                RawDatasetProfile reference
  domain:                         BANKING | HEALTHCARE | INSURANCE | GENERAL | UNKNOWN
  domain_confidence:              HIGH | MEDIUM | LOW
  domain_conflict_flag:           Boolean
  dataset_type:                   TABULAR | TIME_SERIES | PANEL | NLP | CV | GRAPH | UNKNOWN
  dataset_type_confidence:        HIGH | MEDIUM | LOW
  label_type:                     BINARY | MULTICLASS | REGRESSION | NONE | UNKNOWN
  has_target_column:              Boolean
  inferred_target_column:         String or NULL
  has_temporal_column:            Boolean
  temporal_column_name:           String or NULL
  has_group_column:               Boolean
  group_column_name:              String or NULL
  has_pii_detected:               Boolean
  pii_column_candidates:          [list of column names]
  protected_attribute_flag:       Boolean
  protected_attribute_candidates: [list of column names]
  n_rows:                         Integer or UNKNOWN
  n_features:                     Integer
  domain_risk_flag:               LOW | MODERATE | HIGH | CRITICAL
  regulatory_exposure_flag:       Boolean
  high_risk_target_flag:          Boolean
  high_risk_target_name:          String or NULL
  domain_feature_registry_ref:    String
  regulatory_defaults:            REGULATORY_DEFAULTS[domain]
  protected_attributes_registry:  PROTECTED_ATTRIBUTES_BY_DOMAIN[domain]
  escalation_triggers:            [list of escalation codes from SECTION 6]
  classification_timestamp:       ISO timestamp
```

---

## SECTION 9 — GAL Write Specification

Field-by-field mapping from engine output to `DatasetIdentity` Pydantic model in `gal_schema.py`.

| Engine Field | gal_schema.py Field | Type | Notes |
|---|---|---|---|
| `domain` | `DatasetIdentity.domain` | `str` | Must match SECTION 1 enum |
| `domain_confidence` | `DatasetIdentity.domain_confidence` | `str` | `HIGH` \| `MEDIUM` \| `LOW` |
| `domain_conflict_flag` | `DatasetIdentity.domain_conflict_flag` | `bool` | |
| `dataset_type` | `DatasetIdentity.dataset_type` | `str` | Must match SECTION 1 enum |
| `dataset_type_confidence` | `DatasetIdentity.dataset_type_confidence` | `str` | `HIGH` \| `MEDIUM` \| `LOW` |
| `label_type` | `DatasetIdentity.label_type` | `str` | Must match SECTION 1 enum |
| `has_target_column` | `DatasetIdentity.has_target_column` | `bool` | |
| `inferred_target_column` | `DatasetIdentity.inferred_target_column` | `Optional[str]` | NULL if no target |
| `has_temporal_column` | `DatasetIdentity.has_temporal_column` | `bool` | |
| `temporal_column_name` | `DatasetIdentity.temporal_column_name` | `Optional[str]` | |
| `has_group_column` | `DatasetIdentity.has_group_column` | `bool` | |
| `group_column_name` | `DatasetIdentity.group_column_name` | `Optional[str]` | |
| `has_pii_detected` | `DatasetIdentity.has_pii_detected` | `bool` | |
| `pii_column_candidates` | `DatasetIdentity.pii_column_candidates` | `List[str]` | |
| `protected_attribute_flag` | `DatasetIdentity.protected_attribute_flag` | `bool` | |
| `n_rows` | `DatasetIdentity.n_rows` | `Optional[int]` | `UNKNOWN` → `None` |
| `n_features` (= n_columns) | `DatasetIdentity.n_features` | `Optional[int]` | |
| `domain_risk_flag` | `DatasetIdentity.domain_risk_flag` | `str` | Must match SECTION 1 enum |
| `regulatory_exposure_flag` | `DatasetIdentity.regulatory_exposure_flag` | `bool` | |
| `high_risk_target_flag` | `DatasetIdentity.high_risk_target_flag` | `bool` | |
| `high_risk_target_name` | `DatasetIdentity.high_risk_target_name` | `Optional[str]` | NULL if no high-risk target |
| `domain_feature_registry_ref` | `DatasetIdentity.domain_feature_registry_ref` | `str` | Registry URI string |
| `escalation_triggers` | `DatasetIdentity.escalation_triggers` | `List[str]` | Codes from SECTION 6 |
| `classification_timestamp` | `DatasetIdentity.classification_timestamp` | `str` | ISO timestamp |

```python
# HARD_STOP gate: do not write if DATASET_TYPE_CANNOT_BE_INFERRED is active
IF "DATASET_TYPE_CANNOT_BE_INFERRED" IN escalation_triggers:
    RETURN HARD_STOP
    reason = "HARD_STOP escalation active. DatasetIdentity will not be written to GAL."

# GAL write operation
WRITE DatasetIdentity TO GAL
RETURN DatasetIdentity.identity_id
```

