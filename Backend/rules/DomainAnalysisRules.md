# DomainAnalysisRules.md
## Enterprise Domain Analysis and Dataset Identity Engine — Backend Governance Specification
**Version:** 2.0
**Produces:** DatasetIdentity object → stored in GAL
**Consumed by:** QuestionBuilderRules, IntentInferenceRules, DRIL, EPR, DataScienceRules engine
**Constraint:** Classification and inference only. No data cleaning. No transformation.

---

## Input Contract

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

## Output Contract

DatasetIdentity object written to GAL:

```
DatasetIdentity:
  identity_id:              UUID (immutable)
  raw_profile_ref:          RawDatasetProfile reference
  domain:                   BANKING | HEALTHCARE | INSURANCE | GENERAL | UNKNOWN
  domain_confidence:        HIGH | MEDIUM | LOW
  domain_conflict_flag:     Boolean
  dataset_type:             TABULAR | TIME_SERIES | PANEL | NLP | CV | GRAPH | UNKNOWN
  dataset_type_confidence:  HIGH | MEDIUM | LOW
  label_type:               BINARY | MULTICLASS | REGRESSION | NONE | UNKNOWN
  has_target_column:        Boolean
  inferred_target_column:   String or NULL
  has_temporal_column:      Boolean
  temporal_column_name:     String or NULL
  has_group_column:         Boolean
  group_column_name:        String or NULL
  has_pii_detected:         Boolean
  pii_column_candidates:    [list of column names]
  protected_attribute_flag: Boolean
  protected_attribute_candidates: [list of column names]
  n_rows:                   Integer or UNKNOWN
  n_features:               Integer
  domain_risk_flag:         LOW | MODERATE | HIGH | CRITICAL
  regulatory_exposure_flag: Boolean
  high_risk_target_flag:    Boolean
  high_risk_target_name:    String or NULL
  domain_feature_registry_ref: String (pointer to applicable registry section)
  escalation_triggers:      [list of triggered escalation codes]
  classification_timestamp: ISO timestamp
```

---

## Module A — Dataset Type Classification

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
    temporal_column_name = temporal_column_candidates[0]
    # If multiple candidates, select the one with most distinct values
    IF temporal_column_candidates.count > 1:
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

# STEP 3: Dataset type classification
IF has_temporal_column == True AND has_group_column == True:
    dataset_type = PANEL
    dataset_type_confidence = HIGH

ELIF has_temporal_column == True AND has_group_column == False:
    dataset_type = TIME_SERIES
    dataset_type_confidence = MEDIUM
    # Could still be panel if group column is present but not named predictably

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
    # High-dimensional numeric: could be image pixels or embeddings. Escalate.
    escalation_triggers.append("HIGH_DIMENSIONAL_NUMERIC_AMBIGUOUS_CV_OR_TABULAR")

ELSE:
    dataset_type = UNKNOWN
    dataset_type_confidence = LOW
    escalation_triggers.append("DATASET_TYPE_CANNOT_BE_INFERRED")
```

---

## Module B — Target Column and Label Type Inference

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
    
    IF target_dtype in ["bool"] OR set(target_sample).issubset({0, 1, "0", "1", "True", "False", "true", "false", "yes", "no", "Y", "N"}):
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

## Module C — Domain Classification

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
            domain_signals[mapped_domain] += 5  # User statement is strong signal

# STEP 3: Domain assignment
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

# STEP 4: Conflict detection
IF user_stated_domain_parsed IS NOT NULL AND user_stated_domain_parsed != domain AND max_signal < 5:
    domain = user_stated_domain_parsed  # User statement takes precedence when signal is weak
    domain_conflict_flag = True
    escalation_triggers.append("DOMAIN_SIGNAL_CONFLICT_USER_VS_INFERRED")
ELSE:
    domain_conflict_flag = False
```

---

## Module D — PII and Protected Attribute Detection

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

## Module E — Domain Risk Flag Assignment

```python
# HIGH-RISK TARGET DETECTION
HIGH_RISK_TARGETS = {
    BANKING: [
        "default", "pd", "probability_of_default", "default_flag",
        "credit_decision", "loan_approved", "fraud", "is_fraud",
        "aml_flag", "sanction_flag"
    ],
    HEALTHCARE: [
        "mortality", "death", "readmission", "adverse_event",
        "sepsis", "icu_admission", "diagnosis", "cancer", "survival"
    ],
    INSURANCE: [
        "claim", "large_claim", "fraud_claim", "lapse", "loss"
    ]
}

high_risk_target_flag = False
high_risk_target_name = NULL

IF has_target_column == True AND inferred_target_column IS NOT NULL:
    col_lower = inferred_target_column.lower()
    IF domain IN HIGH_RISK_TARGETS:
        FOR target_pattern in HIGH_RISK_TARGETS[domain]:
            IF target_pattern in col_lower:
                high_risk_target_flag = True
                high_risk_target_name = inferred_target_column

# DOMAIN RISK FLAG MATRIX
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
    # Healthcare is never LOW regardless of target

ELIF domain == INSURANCE:
    IF high_risk_target_flag == True:
        domain_risk_flag = HIGH
    ELIF protected_attribute_flag == True:
        domain_risk_flag = HIGH
    ELSE:
        domain_risk_flag = MODERATE

ELSE: # GENERAL
    IF protected_attribute_flag == True AND label_type in [BINARY, MULTICLASS]:
        domain_risk_flag = MODERATE
    ELSE:
        domain_risk_flag = LOW

# REGULATORY EXPOSURE FLAG
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

## Module F — Domain Feature Registry Reference

Domain feature registries define which features carry elevated governance requirements. These are referenced — not executed — by DomainAnalysisRules.

```
domain_feature_registry_ref assignment:

IF domain == BANKING:
    domain_feature_registry_ref = "registry://banking/v2"
    
    BANKING REGISTRY CONCEPTUAL STRUCTURE:
    
    regulatory_capital_features:
      # Features used in Basel capital calculation — no imputation without MRM approval
      - pd_score, lgd_estimate, ead_value, exposure_at_default,
        collateral_value, risk_weight, ecl_provision
    
    high_sensitivity_features:
      # Features that proxy for creditworthiness — require leakage review
      - bureau_score, internal_score, delinquency_count, days_past_due,
        utilization_rate, credit_limit, revolving_balance
    
    prohibited_for_credit_decisions:
      # Cannot be used in models that determine credit access
      # Source: ECOA, Fair Credit Reporting Act, national equivalents
      - race, ethnicity, gender, age (unless legally permitted), religion,
        national_origin, marital_status, zip_code (if proxy for race)

ELIF domain == HEALTHCARE:
    domain_feature_registry_ref = "registry://healthcare/v2"
    
    HEALTHCARE REGISTRY CONCEPTUAL STRUCTURE:
    
    clinical_features:
      # Missing values clinically significant — trigger Module 3 hard stop
      - lab_results, vitals, medications, procedures, diagnoses
    
    high_sensitivity_features:
      # PHI under HIPAA — access restricted
      - patient_id, date_of_birth, address, mrn, ssn, device_identifiers
    
    high_risk_outcome_features:
      # FN cost floor = 10x FP cost unless overridden in Business Decision Charter
      - mortality, adverse_event, sepsis_flag, icu_admission, readmission_30d

ELIF domain == INSURANCE:
    domain_feature_registry_ref = "registry://insurance/v2"
    
    INSURANCE REGISTRY CONCEPTUAL STRUCTURE:
    
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

## Module G — Protected Attribute Registry by Domain

```
PROTECTED_ATTRIBUTES_BY_DOMAIN = {

    BANKING: {
        legally_protected: [
            "race", "color", "religion", "national_origin", "sex",
            "marital_status", "age", "familial_status", "disability"
        ],
        proxy_risk_high: [
            "zip_code", "postal_code", "neighborhood", "surname",
            "first_name", "language_preference"
        ],
        regulatory_source: ["ECOA", "FHA", "FCRA", "national equivalents"]
    },

    HEALTHCARE: {
        legally_protected: [
            "race", "color", "national_origin", "sex", "age",
            "disability", "religion"
        ],
        proxy_risk_high: [
            "zip_code", "insurance_type", "language", "socioeconomic_indicator"
        ],
        regulatory_source: ["Section 1557 ACA", "HIPAA", "national equivalents"]
    },

    INSURANCE: {
        legally_protected: [
            "race", "color", "religion", "national_origin", "sex",
            "marital_status", "age", "disability"
        ],
        proxy_risk_high: [
            "zip_code", "credit_score (in some jurisdictions)", "occupation"
        ],
        regulatory_source: ["State insurance codes", "national equivalents"]
    },

    GENERAL: {
        legally_protected: [
            "race", "gender", "age", "disability", "religion",
            "national_origin", "pregnancy"
        ],
        proxy_risk_high: [
            "zip_code", "name", "language"
        ],
        regulatory_source: ["GDPR Article 9", "national equivalents"]
    }
}
```

---

## Module H — Regulatory Defaults by Domain

```python
REGULATORY_DEFAULTS = {

    BANKING: {
        regulatory_mode_default:       REGULATED,
        regulatory_frameworks:         [SR_11_7],
        imv_separation_required:       True,
        approval_expiry_tier1_days:    180,
        approval_expiry_tier2_days:    365,
        audit_log_retention_years:     7,
        fairness_di_threshold:         0.80,
        model_inventory_required:      True,
        challenger_framework_required: True
    },

    HEALTHCARE: {
        regulatory_mode_default:       REGULATED,
        regulatory_frameworks:         [SECTOR_CLINICAL],
        imv_separation_required:       True,
        approval_expiry_tier1_days:    180,
        approval_expiry_tier2_days:    365,
        audit_log_retention_years:     10,
        fairness_di_threshold:         0.80,
        minimum_recall_floor:          0.85,
        model_inventory_required:      True,
        challenger_framework_required: False
    },

    INSURANCE: {
        regulatory_mode_default:       REGULATED,
        regulatory_frameworks:         [SECTOR_CLINICAL],
        imv_separation_required:       True,
        approval_expiry_tier1_days:    365,
        approval_expiry_tier2_days:    365,
        audit_log_retention_years:     7,
        fairness_di_threshold:         0.80,
        model_inventory_required:      True,
        challenger_framework_required: True
    },

    GENERAL: {
        regulatory_mode_default:       STANDARD,
        regulatory_frameworks:         [NONE],
        imv_separation_required:       False,
        approval_expiry_tier1_days:    365,
        approval_expiry_tier2_days:    730,
        audit_log_retention_years:     3,
        fairness_di_threshold:         0.80,
        model_inventory_required:      False,
        challenger_framework_required: False
    }
}

# Apply regulatory defaults to DatasetIdentity for consumption by downstream modules
DatasetIdentity.regulatory_defaults = REGULATORY_DEFAULTS[domain]
```

---

## Module I — Domain-Specific Escalation Triggers

```python
# Run after all modules complete

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
        "code": "PII_IN_FEATURE_SET",
        "condition": has_pii_detected == True,
        "reason": "PII columns detected. Access controls and GDPR processing basis must be verified.",
        "action": "HALT_UNTIL_DATA_GOVERNANCE_CLEARED"
    },
    {
        "code": "DATASET_TYPE_UNKNOWN",
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
        "code": "DOMAIN_CONFLICT",
        "condition": domain_conflict_flag == True,
        "reason": "User-stated domain conflicts with inferred domain. Governance defaults may be misapplied.",
        "action": "RESOLVE_DOMAIN_BEFORE_DOWNSTREAM_PROCESSING"
    },
    {
        "code": "PROTECTED_ATTRIBUTES_IN_BANKING_CREDIT",
        "condition": domain == BANKING AND high_risk_target_flag == True AND protected_attribute_flag == True,
        "reason": "Protected attributes detected in banking credit model dataset. ECOA compliance assessment required.",
        "action": "NOTIFY_COMPLIANCE_BEFORE_FEATURE_ENGINEERING"
    },
    {
        "code": "HEALTHCARE_MORTALITY_TARGET",
        "condition": domain == HEALTHCARE AND high_risk_target_name IS NOT NULL AND any(["mortality", "death", "sepsis"] in high_risk_target_name.lower()),
        "reason": "Life-critical outcome target detected. FN cost floor and minimum recall floor apply.",
        "action": "REQUIRE_CLINICAL_SME_AND_ETHICS_REVIEW"
    }
]

FOR each rule in ESCALATION_RULES:
    IF rule.condition == True:
        escalation_triggers.append(rule.code)
        # Triggers do not halt DomainAnalysisRules output
        # They are carried in DatasetIdentity and evaluated by downstream modules
```

---

## Module J — DatasetIdentity Assembly and GAL Write

```python
# Final assembly of DatasetIdentity object

DatasetIdentity = {
    identity_id:                   generate_uuid(),
    raw_profile_ref:               RawDatasetProfile.ref,
    domain:                        domain,
    domain_confidence:             domain_confidence,
    domain_conflict_flag:          domain_conflict_flag,
    dataset_type:                  dataset_type,
    dataset_type_confidence:       dataset_type_confidence,
    label_type:                    label_type,
    has_target_column:             has_target_column,
    inferred_target_column:        inferred_target_column,
    has_temporal_column:           has_temporal_column,
    temporal_column_name:          temporal_column_name,
    has_group_column:              has_group_column,
    group_column_name:             group_column_name,
    has_pii_detected:              has_pii_detected,
    pii_column_candidates:         pii_column_candidates,
    protected_attribute_flag:      protected_attribute_flag,
    protected_attribute_candidates: protected_attribute_candidates,
    n_rows:                        n_rows,
    n_features:                    n_columns,
    domain_risk_flag:              domain_risk_flag,
    regulatory_exposure_flag:      regulatory_exposure_flag,
    high_risk_target_flag:         high_risk_target_flag,
    high_risk_target_name:         high_risk_target_name,
    domain_feature_registry_ref:   domain_feature_registry_ref,
    regulatory_defaults:           REGULATORY_DEFAULTS[domain],
    protected_attributes_registry: PROTECTED_ATTRIBUTES_BY_DOMAIN[domain],
    escalation_triggers:           escalation_triggers,
    classification_timestamp:      ingest_timestamp
}

WRITE DatasetIdentity TO GAL
RETURN DatasetIdentity.identity_id
```
