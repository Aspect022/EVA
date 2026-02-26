# EVA Data Science Rules
## Strategy Agent Reference Guide

# EVA — Backend Rule Engine Specification
## Phase-by-Phase Executable Decision Logic

**Version:** 1.0  
**Classification:** Internal — Model Risk / ML Platform  
**Scope:** Modules 1–10 covering full ML governance decision surface  
**Format:** Executable IF–ELSE routing logic with threshold values, tier conditions, and failure modes

---

## Global Constants and Enumerations

```
RISK_TIER:
  TIER_1 = "high_risk_automated"       # No human review, legal/financial impact
  TIER_2 = "medium_risk_human_reviewed" # Human reviews final decision
  TIER_3 = "low_risk_analytical"        # Insight/reporting only

DATASET_TYPE:
  TABULAR = "tabular"
  TIME_SERIES = "time_series"
  PANEL = "panel"
  NLP = "nlp"
  CV = "computer_vision"
  GRAPH = "graph"

DOMAIN:
  BANKING = "banking"
  HEALTHCARE = "healthcare"
  INSURANCE = "insurance"
  GENERAL = "general"

REGULATORY_MODE:
  STANDARD = "standard"
  REGULATED = "regulated"    # EU AI Act Annex III, SR 11-7 active
  GDPR_STRICT = "gdpr_strict"

SYSTEM_MODE:
  STARTUP = "startup"         # <5 person team, MVP phase
  ENTERPRISE = "enterprise"   # Full platform, all planes active
  REGULATED = "regulated"     # All controls + external audit trail

HARD_STOP = "PIPELINE_HALT_REQUIRE_HUMAN_RESOLUTION"
SOFT_WARN = "LOG_ALERT_CONTINUE_WITH_FLAG"
```

---

## Module 1 — Data Contract and Provenance

### Inputs

```
dataset_id:             UUID of incoming dataset
source_system_id:       Identifier of originating system
schema_contract_path:   Path to expected schema YAML
lineage_metadata:       {source, extraction_timestamp, owner, approved_version}
pii_manifest_path:      Path to declared PII columns (if exists)
business_charter_id:    UUID of governing Business Decision Charter
regulatory_mode:        STANDARD | REGULATED | GDPR_STRICT
risk_tier:              TIER_1 | TIER_2 | TIER_3
```

### Decision Logic

```python
# STEP 1: Business Decision Charter verification
IF business_charter_id IS NULL OR NOT EXISTS IN charter_registry:
    RETURN HARD_STOP
    reason = "No governing Business Decision Charter. Module 1 will not accept data without charter."
    escalate_to = ["ML_LEAD", "MODEL_RISK"]

# STEP 2: Source system authentication
IF source_system_id NOT IN approved_source_registry:
    RETURN HARD_STOP
    reason = "Source system not in approved registry."
    escalate_to = ["DATA_ENGINEERING", "MODEL_RISK"]

# STEP 3: Lineage completeness
IF lineage_metadata.extraction_timestamp IS NULL:
    RETURN HARD_STOP
    reason = "Cannot verify data freshness without extraction timestamp."

IF lineage_metadata.approved_version IS NULL:
    IF regulatory_mode IN [REGULATED, GDPR_STRICT]:
        RETURN HARD_STOP
        reason = "Regulated mode requires versioned dataset approval."
    ELSE:
        RETURN SOFT_WARN
        flag = "LINEAGE_VERSION_MISSING"

# STEP 4: Schema validation
IF schema_contract_path IS NULL:
    IF risk_tier == TIER_1:
        RETURN HARD_STOP
        reason = "Tier 1 models require a schema contract before data intake."
    ELSE:
        RETURN SOFT_WARN
        flag = "SCHEMA_CONTRACT_MISSING"
        proceed = True

ELSE:
    run schema_validation(dataset_id, schema_contract_path)
    
    IF schema_validation.column_count_mismatch == True:
        RETURN HARD_STOP
        reason = "Column count mismatch against contract. Silent schema mutation detected."

    IF schema_validation.type_mutations > 0:
        RETURN HARD_STOP
        reason = f"{schema_validation.type_mutations} column type mutations detected."

    IF schema_validation.new_null_columns > 0 AND risk_tier == TIER_1:
        RETURN HARD_STOP
        reason = "New null columns in Tier 1 dataset. Requires investigation."

    IF schema_validation.new_null_columns > 0 AND risk_tier IN [TIER_2, TIER_3]:
        RETURN SOFT_WARN
        flag = "NEW_NULL_COLUMNS_DETECTED"

# STEP 5: PII detection and tagging
run pii_scan(dataset_id)

IF pii_scan.detected_pii_columns NOT IN pii_manifest:
    undeclared = pii_scan.detected_pii_columns - pii_manifest.declared_columns
    IF undeclared.count > 0:
        IF regulatory_mode IN [REGULATED, GDPR_STRICT]:
            RETURN HARD_STOP
            reason = f"{undeclared.count} undeclared PII columns detected."
            action = "Tag columns, restrict access, notify Compliance."
        ELSE:
            RETURN SOFT_WARN
            flag = "UNDECLARED_PII_DETECTED"
            action = "Auto-tag columns, notify Data Engineering."

# STEP 6: Data freshness validation
data_age_days = today - lineage_metadata.extraction_timestamp

IF domain == BANKING AND data_age_days > 30:
    RETURN SOFT_WARN
    flag = "STALE_DATA_BANKING"

IF domain == HEALTHCARE AND data_age_days > 90:
    RETURN SOFT_WARN
    flag = "STALE_DATA_HEALTHCARE"

IF data_age_days > 365:
    RETURN HARD_STOP
    reason = "Dataset older than 365 days. Cannot validate representativeness."

# STEP 7: Repeated source failure check
source_failure_count = get_rolling_failure_count(source_system_id, window_days=30)

IF source_failure_count >= 3:
    RETURN HARD_STOP
    reason = "Source system failed provenance 3+ times in 30 days."
    escalate_to = ["DATA_ENGINEERING"]
    remediation_sla_days = 10

# STEP 8: Issue provenance certificate
IF all checks passed OR only SOFT_WARN flags:
    issue provenance_certificate(
        dataset_id,
        schema_validation_result,
        pii_manifest_final,
        lineage_hash,
        flags=[accumulated soft warnings],
        signed_by="MODULE_1_SERVICE"
    )
    write_to_registry(dataset_id, provenance_certificate)
    RETURN PROCEED
```

### Escalation Rules

```
HARD_STOP → notify ["DATA_ENGINEERING", "MODEL_RISK"] via alert channel within 5 minutes
SOFT_WARN accumulation >= 3 flags → escalate to ML_LEAD for review before proceeding
Source failure count >= 3 → assign human owner, SLA = 10 business days
```

### Failure Handling

```
HARD_STOP: Pipeline halts. No downstream module executes. Ticket created automatically.
           Failure logged to audit trail with timestamp, reason, dataset_id, source_system_id.
SOFT_WARN: Pipeline continues. Flag appended to provenance certificate.
           Flags visible in all downstream module inputs.
           Model card inherits all flags from provenance certificate.
```

### Mode-Specific Overrides

```
Startup Mode:
  - PII detection: SOFT_WARN instead of HARD_STOP for undeclared PII
  - Schema contract: Optional for TIER_2 and TIER_3
  - Source registry: Warn-only for unregistered sources

Enterprise Mode:
  - All defaults apply as specified above

Regulated Mode:
  - Schema contract: REQUIRED for ALL tiers, no exceptions
  - Lineage version: REQUIRED, no soft warn path
  - PII: HARD_STOP for any undeclared PII regardless of count
  - Provenance certificate: Must include regulatory_mode flag for audit
  - Source registry: HARD_STOP for any unregistered source
```

---

## Module 2 — Feature Engineering and Governance

### Inputs

```
provenance_certificate:         Signed output from Module 1
feature_spec_registry:          Approved features for this use_case_id
business_charter:               Cost matrix, temporal boundary, domain, risk_tier
protected_attribute_list:       Maintained by Compliance, domain-specific
dataset_type:                   TABULAR | TIME_SERIES | PANEL | NLP | CV | GRAPH
n_rows:                         Integer, dataset row count
n_columns:                      Integer, dataset column count
target_column:                  Name of prediction target
decision_timestamp_column:      Name of column representing decision time (required for time-aware)
regulatory_mode:                STANDARD | REGULATED | GDPR_STRICT
```

### Decision Logic

```python
# STEP 1: Validate provenance certificate
IF provenance_certificate IS NULL OR provenance_certificate.signed_by != "MODULE_1_SERVICE":
    RETURN HARD_STOP
    reason = "Missing or invalid provenance certificate. Module 1 must run first."

IF "SCHEMA_CONTRACT_MISSING" IN provenance_certificate.flags AND risk_tier == TIER_1:
    RETURN HARD_STOP
    reason = "Cannot engineer features for Tier 1 model without schema contract."

# STEP 2: Temporal integrity enforcement
IF dataset_type IN [TIME_SERIES, PANEL]:
    IF decision_timestamp_column IS NULL:
        RETURN HARD_STOP
        reason = "Time-series/panel data requires explicit decision_timestamp_column."

    FOR each feature in proposed_features:
        IF feature.uses_data_after(decision_timestamp - availability_buffer_hours):
            quarantine_feature(feature)
            IF risk_tier == TIER_1:
                RETURN HARD_STOP
                reason = f"Temporal leakage in feature {feature.name}. Data used after decision timestamp."
            ELSE:
                RETURN SOFT_WARN
                flag = f"TEMPORAL_BOUNDARY_VIOLATION_{feature.name}"

    availability_buffer_hours:
        BANKING: 24
        HEALTHCARE: 48
        INSURANCE: 24
        GENERAL: 12

# STEP 3: Leakage detection
FOR each feature in proposed_features:
    mi_score = compute_mutual_information(feature, target_column)
    
    IF mi_score > 0.85:
        quarantine_feature(feature)
        create_leakage_review_ticket(feature, mi_score)
        IF risk_tier == TIER_1:
            RETURN HARD_STOP
            reason = f"Feature {feature.name} MI score {mi_score} exceeds 0.85. Quarantined pending review."
            review_required_from = ["SENIOR_ML_ENGINEER", "MODEL_RISK_ANALYST"]
            review_sla_days = 3
        ELSE:
            RETURN SOFT_WARN
            flag = f"HIGH_MI_FEATURE_{feature.name}"
            flag_detail = f"MI score: {mi_score}. Review recommended."

    IF mi_score > 0.95:
        RETURN HARD_STOP
        reason = f"Feature {feature.name} MI score {mi_score} exceeds 0.95. Near-perfect leakage."
        # No tier exception. Hard stop regardless.

# STEP 4: Protected attribute proxy detection
FOR each feature in proposed_features:
    FOR each protected_attr in protected_attribute_list:
        corr = compute_correlation(feature, protected_attr)
        
        IF corr > 0.7:
            IF risk_tier == TIER_1:
                BLOCK_FEATURE(feature)
                log_block(feature, reason=f"Proxy for {protected_attr}, correlation={corr}")
                # Hard block, no override path for Tier 1
            ELSE IF risk_tier == TIER_2:
                IF regulatory_mode == REGULATED:
                    BLOCK_FEATURE(feature)
                    log_block(feature, reason=f"Regulated mode proxy block. Correlation={corr}")
                ELSE:
                    RETURN SOFT_WARN
                    flag = f"PROXY_RISK_{feature.name}_{protected_attr}"
            ELSE: # TIER_3
                RETURN SOFT_WARN
                flag = f"PROXY_RISK_{feature.name}_{protected_attr}"

IF blocked_features.count > 0.20 * proposed_features.count:
    RETURN HARD_STOP
    reason = f"{blocked_features.count} features blocked. >20% of feature set. Pipeline halted."
    escalate_to = ["ML_LEAD", "MODEL_RISK"]

# STEP 5: High cardinality check
FOR each categorical_feature in proposed_features:
    cardinality = compute_cardinality(categorical_feature)
    n_rows = dataset.n_rows
    
    IF cardinality > 0.5 * n_rows:
        RETURN HARD_STOP
        reason = f"Feature {categorical_feature.name} cardinality {cardinality} exceeds 50% of row count. Explosion risk."
    
    IF cardinality > 100 AND n_rows < 10000:
        RETURN SOFT_WARN
        flag = f"HIGH_CARDINALITY_SMALL_DATASET_{categorical_feature.name}"

# STEP 6: Ratio and aggregation governance
FOR each derived_feature in proposed_features:
    IF derived_feature.type == "RATIO":
        IF derived_feature.denominator_can_be_zero:
            RETURN HARD_STOP
            reason = f"Ratio feature {derived_feature.name} has unguarded zero denominator."
    
    IF derived_feature.type == "ROLLING_AGGREGATE":
        IF derived_feature.window_definition IS NULL:
            RETURN HARD_STOP
            reason = f"Rolling aggregate {derived_feature.name} has no window definition."

# STEP 7: Write to Feature Store
IF all checks passed:
    write_feature_snapshot(
        feature_matrix,
        snapshot_id = generate_uuid(),
        feature_documentation = auto_generate_docs(features),
        provenance_cert_id = provenance_certificate.id,
        blocked_features = blocked_features,
        flags = accumulated_flags
    )
    RETURN PROCEED
```

### Escalation Rules

```
Leakage review unresolved after 3 business days → pipeline administratively cancelled
Leakage rejection twice for same issue → escalate to Model Risk Committee for scope review
>20% features blocked → escalate to ML_LEAD + MODEL_RISK within 1 hour
```

### Failure Handling

```
HARD_STOP: Feature pipeline halts. Quarantined features logged with MI score, timestamp, reviewer assignment.
SOFT_WARN: Feature flagged in documentation. Flag propagates to model card.
Blocked features: Never deleted. Logged permanently with reason and timestamp.
```

### Mode-Specific Overrides

```
Startup Mode:
  - Protected attribute proxy: SOFT_WARN for TIER_2, allow with documentation
  - High cardinality: SOFT_WARN only, no hard stop
  - Ratio zero-denominator: SOFT_WARN with engineering note

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - All proxy correlations > 0.5 (lowered from 0.7) trigger block for TIER_1 and TIER_2
  - All derived features require explicit approval entry in feature_spec_registry
  - Rolling windows: must be documented in feature_spec_registry before use
```

---

## Module 3 — Missing Data Routing

### Inputs

```
feature_snapshot_id:        Versioned Feature Store snapshot ID
missing_profile:            {column_name: missing_pct} for all columns
target_column:              Name of prediction target
dataset_type:               TABULAR | TIME_SERIES | PANEL
n_rows:                     Integer
risk_tier:                  TIER_1 | TIER_2 | TIER_3
domain:                     BANKING | HEALTHCARE | INSURANCE | GENERAL
regulatory_mode:            STANDARD | REGULATED | GDPR_STRICT
```

### Decision Logic

```python
# STEP 1: Per-column missing percentage routing
FOR each column in feature_snapshot:
    missing_pct = missing_profile[column]
    
    # TIER 1 thresholds
    IF risk_tier == TIER_1:
        IF missing_pct > 0.40:
            DROP_COLUMN(column)
            log_drop(column, reason=f"Missing {missing_pct*100:.1f}% exceeds Tier 1 limit of 40%")
        
        ELIF missing_pct > 0.20:
            IF column in high_risk_feature_list:
                RETURN HARD_STOP
                reason = f"High-risk feature {column} missing {missing_pct*100:.1f}%. No imputation for high-risk features above 20%."
            ELSE:
                route_to = determine_imputation_method(column, dataset_type, missing_pct)
        
        ELIF missing_pct > 0.05:
            route_to = determine_imputation_method(column, dataset_type, missing_pct)
        
        ELIF missing_pct > 0.01:
            route_to = SIMPLE_IMPUTATION
        
        ELSE: # < 1%
            route_to = MEDIAN_MEAN_MODE_BY_TYPE
    
    # TIER 2 thresholds
    ELIF risk_tier == TIER_2:
        IF missing_pct > 0.60:
            DROP_COLUMN(column)
        ELIF missing_pct > 0.30:
            route_to = determine_imputation_method(column, dataset_type, missing_pct)
        ELIF missing_pct > 0.05:
            route_to = SIMPLE_IMPUTATION
        ELSE:
            route_to = MEDIAN_MEAN_MODE_BY_TYPE
    
    # TIER 3 thresholds
    ELSE:
        IF missing_pct > 0.80:
            DROP_COLUMN(column)
        ELIF missing_pct > 0.50:
            route_to = MULTIPLE_IMPUTATION
        ELSE:
            route_to = SIMPLE_IMPUTATION

# STEP 2: Imputation method routing
FUNCTION determine_imputation_method(column, dataset_type, missing_pct):
    
    # Mechanism inference
    mechanism = infer_missing_mechanism(column)
    # mechanism: MCAR | MAR | MNAR
    
    IF mechanism == MNAR:
        # Missing not at random: imputation biases the signal
        IF risk_tier == TIER_1:
            RETURN HARD_STOP
            reason = f"Column {column} is MNAR. Imputation in Tier 1 prohibited for MNAR without Model Risk sign-off."
        ELIF risk_tier == TIER_2:
            RETURN SOFT_WARN
            flag = f"MNAR_IMPUTATION_RISK_{column}"
            # Proceed with null-as-signal encoding
            route_to = NULL_AS_SIGNAL_ENCODE
        ELSE:
            route_to = NULL_AS_SIGNAL_ENCODE
    
    IF dataset_type IN [TIME_SERIES, PANEL]:
        IF mechanism == MCAR:
            route_to = FORWARD_FILL  # time-aware
        ELIF mechanism == MAR:
            route_to = INTERPOLATION_WITH_TEMPORAL_BOUND
        ELSE:
            route_to = NULL_AS_SIGNAL_ENCODE
    
    ELIF dataset_type == TABULAR:
        IF missing_pct < 0.05:
            IF column.dtype == NUMERIC:
                route_to = MEDIAN_IMPUTATION
            ELSE:
                route_to = MODE_IMPUTATION
        
        ELIF missing_pct >= 0.05 AND missing_pct < 0.20:
            IF mechanism == MCAR:
                route_to = MEDIAN_IMPUTATION
            ELIF mechanism == MAR:
                route_to = MODEL_BASED_IMPUTATION  # KNN or iterative
        
        ELIF missing_pct >= 0.20:
            IF n_rows > 10000:
                route_to = MULTIPLE_IMPUTATION
            ELSE:
                route_to = SOFT_WARN
                flag = f"HIGH_MISSING_SMALL_DATASET_{column}"
                route_to = MEDIAN_IMPUTATION  # only viable option
    
    RETURN route_to

# STEP 3: Target column missing check
IF missing_profile[target_column] > 0.0:
    IF missing_pct > 0.05:
        RETURN HARD_STOP
        reason = f"Target column missing {missing_pct*100:.1f}%. Cannot train with missing target labels."
    ELSE:
        DROP_ROWS where target_column IS NULL
        log_action(f"Dropped {dropped_count} rows with null target.")

# STEP 4: Domain-specific overrides
IF domain == HEALTHCARE:
    # In clinical data, missing lab value is clinically significant
    # Promote all SOFT_WARN for clinical features to HARD_STOP requiring clinical SME review
    FOR each clinical_feature IN domain_feature_registry.clinical:
        IF column == clinical_feature AND missing_pct > 0.10:
            RETURN HARD_STOP
            reason = f"Clinical feature {column} missing {missing_pct*100:.1f}%. Requires clinical SME sign-off."

IF domain == BANKING:
    # Regulatory capital features cannot be imputed without MRM approval
    FOR each regulatory_feature IN domain_feature_registry.regulatory_capital:
        IF column == regulatory_feature AND missing_pct > 0.0:
            RETURN HARD_STOP
            reason = f"Regulatory capital feature {column} has any missing values. Cannot impute."

# STEP 5: Post-imputation audit log
FOR each imputed_column:
    log_imputation(
        column = column,
        method = route_to,
        missing_pct_before = missing_profile[column],
        mechanism_inferred = mechanism,
        n_rows_affected = imputed_row_count,
        timestamp = now()
    )
```

### Escalation Rules

```
MNAR feature in Tier 1 HARD_STOP → escalate to MODEL_RISK_ANALYST + ML_LEAD, SLA 48 hours
>30% of features dropped due to missingness → escalate to DATA_ENGINEERING + ML_LEAD
Healthcare clinical feature HARD_STOP → requires clinical SME, SLA 5 business days
```

### Failure Handling

```
HARD_STOP: Pipeline halts. Imputation log written with reason.
Column drop: Permanent log entry. Never silently dropped.
Imputation audit log: Written regardless of outcome. Referenced in model card.
```

### Mode-Specific Overrides

```
Startup Mode:
  - MNAR in Tier 1: SOFT_WARN + null-as-signal encode (no hard stop)
  - Missing target > 5%: SOFT_WARN, allow row-drop with documentation

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - Any imputation of features used in regulatory capital calculations: HARD_STOP
  - Multiple imputation required (not optional) for missing_pct > 15% in TIER_1
  - Imputation audit log must be stored with model artifact for full model lifecycle
```

---

## Module 4 — Encoding Routing

### Inputs

```
feature_snapshot_id:        Versioned Feature Store snapshot ID
column_profiles:            {column_name: {dtype, cardinality, missing_pct, is_protected}}
target_column:              Name of prediction target
n_rows:                     Integer
dataset_type:               TABULAR | TIME_SERIES | PANEL
risk_tier:                  TIER_1 | TIER_2 | TIER_3
regulatory_mode:            STANDARD | REGULATED | GDPR_STRICT
```

### Decision Logic

```python
FOR each categorical_column in feature_snapshot:
    cardinality = column_profiles[column].cardinality
    is_protected = column_profiles[column].is_protected
    n_rows = dataset.n_rows
    
    # STEP 1: Protected attribute encoding gate
    IF is_protected == True:
        IF risk_tier == TIER_1:
            RETURN HARD_STOP
            reason = f"Protected attribute {column} cannot be encoded for Tier 1 model. Must be blocked at Module 2."
            # This should not reach Module 4. If it does, Module 2 failed.
        ELSE:
            RETURN SOFT_WARN
            flag = f"PROTECTED_ATTR_ENCODING_{column}"
            # Encode as indicator only, no target encoding
            route_to = BINARY_INDICATOR_ENCODING

    # STEP 2: Low cardinality (<=5 unique values)
    ELIF cardinality <= 5:
        route_to = ONE_HOT_ENCODING
    
    # STEP 3: Medium cardinality (6–50 unique values)
    ELIF cardinality <= 50:
        IF risk_tier == TIER_1:
            route_to = ONE_HOT_ENCODING
            # No target encoding for Tier 1: leakage and instability risk
        ELIF n_rows < 5000:
            route_to = ONE_HOT_ENCODING
            # Small dataset: target encoding variance too high
        ELSE:
            route_to = ORDINAL_ENCODING
            # Target encoding requires explicit approval gate below
    
    # STEP 4: High cardinality (51–500 unique values)
    ELIF cardinality <= 500:
        IF risk_tier == TIER_1:
            route_to = TARGET_ENCODING_WITH_REGULARIZATION
            # Allowed but must pass target encoding gate below
        ELIF n_rows < 10000:
            route_to = FREQUENCY_ENCODING
            # Target encoding on small data: too noisy
        ELSE:
            route_to = TARGET_ENCODING_WITH_REGULARIZATION
    
    # STEP 5: Very high cardinality (501–5000 unique values)
    ELIF cardinality <= 5000:
        IF cardinality > 0.1 * n_rows:
            RETURN SOFT_WARN
            flag = f"CARDINALITY_EXCEEDS_10PCT_ROWCOUNT_{column}"
        route_to = HASHING_ENCODING
        # Hashing only. One-hot is infeasible. Target encoding unstable.
    
    # STEP 6: Extreme cardinality (>5000 unique values)
    ELSE: # cardinality > 5000
        IF cardinality > 0.5 * n_rows:
            RETURN HARD_STOP
            reason = f"Column {column} cardinality {cardinality} > 50% of row count. Drop or aggregate before encoding."
        ELSE:
            route_to = HASHING_ENCODING
            RETURN SOFT_WARN
            flag = f"EXTREME_CARDINALITY_{column}"

    # STEP 7: Target encoding regularization gate
    IF route_to == TARGET_ENCODING_WITH_REGULARIZATION:
        IF regulatory_mode == REGULATED:
            require_approval_from = "MODEL_RISK"
            IF approval_status != APPROVED:
                route_to = ORDINAL_ENCODING
                RETURN SOFT_WARN
                flag = f"TARGET_ENCODING_DOWNGRADED_NO_APPROVAL_{column}"
        
        # Apply smoothing parameter
        smoothing_alpha = compute_smoothing_alpha(n_rows, cardinality)
        # smoothing_alpha = max(1.0, n_rows / (cardinality * 10))
        
        IF smoothing_alpha < 1.0:
            RETURN HARD_STOP
            reason = f"Insufficient data for stable target encoding on {column}. Alpha={smoothing_alpha}."

# STEP 8: Numeric encoding routing
FOR each numeric_column in feature_snapshot:
    skewness = compute_skewness(numeric_column)
    kurtosis = compute_kurtosis(numeric_column)
    has_outliers = detect_outliers_iqr(numeric_column)
    
    IF abs(skewness) > 2.0:
        IF domain in [BANKING, INSURANCE]:
            # Finance: log transform preserves economic interpretation
            route_to = LOG1P_TRANSFORM
        ELSE:
            route_to = YEO_JOHNSON_TRANSFORM
    
    ELIF kurtosis > 7.0:
        route_to = ROBUST_SCALER
        # Heavy-tailed: standard scaler distorted by extremes
    
    ELIF has_outliers == True:
        IF domain == BANKING AND numeric_column IN domain_feature_registry.loss_given_default:
            route_to = NO_WINSORIZATION
            # Never winsorize LGD or EAD features in banking models
            RETURN SOFT_WARN
            flag = f"OUTLIERS_PRESENT_NO_WINSORIZATION_{numeric_column}"
        ELSE:
            winsorize_limits = compute_winsorize_limits(risk_tier)
            # TIER_1: (0.01, 0.99), TIER_2: (0.005, 0.995), TIER_3: (0.01, 0.99)
            route_to = WINSORIZATION
    
    ELSE:
        route_to = STANDARD_SCALER

# STEP 9: Datetime encoding
FOR each datetime_column in feature_snapshot:
    IF dataset_type == TIME_SERIES:
        route_to = CYCLICAL_ENCODING  # sin/cos for hour, day, month
    ELSE:
        extract_components = [YEAR, MONTH, DAY_OF_WEEK, QUARTER]
        route_to = COMPONENT_EXTRACTION
```

### Escalation Rules

```
Protected attribute reaching Module 4 → immediate escalation to MODULE_2_OWNER, treated as Module 2 failure
Target encoding approval request → MODEL_RISK, SLA 2 business days
```

### Failure Handling

```
HARD_STOP: Encoding pipeline halts for that column. Downstream training cannot proceed.
SOFT_WARN: Encoding applied with flag. Flag propagates to model card and feature documentation.
Encoding method logged: Every column's final encoding method recorded with rationale.
```

### Mode-Specific Overrides

```
Startup Mode:
  - Target encoding: No approval required, smoothing applied automatically
  - Extreme cardinality: SOFT_WARN only, hashing applied

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - Target encoding: Requires written MODEL_RISK approval for all tiers
  - No hashing encoding for Tier 1 models (interpretability requirement)
  - All encoding choices logged to audit trail with rationale
```

---

## Module 5 — Feature Selection

### Inputs

```
feature_snapshot_id:        Encoded Feature Store snapshot ID
n_rows:                     Integer
n_features:                 Integer, post-encoding feature count
target_column:              Name of prediction target
dataset_type:               TABULAR | TIME_SERIES | PANEL
risk_tier:                  TIER_1 | TIER_2 | TIER_3
interpretability_tier:      1 | 2 | 3 (from Business Decision Charter)
regulatory_mode:             STANDARD | REGULATED | GDPR_STRICT
model_family_candidates:    List of model families under consideration
```

### Decision Logic

```python
# STEP 1: Dataset size classification
IF n_rows < 500:
    dataset_size = "VERY_SMALL"
ELIF n_rows < 5000:
    dataset_size = "SMALL"
ELIF n_rows < 100000:
    dataset_size = "MEDIUM"
ELIF n_rows < 10000000:
    dataset_size = "LARGE"
ELSE:
    dataset_size = "EXTREME"

# STEP 2: Feature-to-row ratio check
feature_ratio = n_features / n_rows

IF feature_ratio > 0.10 AND dataset_size in ["VERY_SMALL", "SMALL"]:
    RETURN HARD_STOP
    reason = f"Feature ratio {feature_ratio:.2f} is too high for dataset size {n_rows} rows. Dimensionality reduction or feature pruning required."

IF feature_ratio > 0.01 AND dataset_size == "MEDIUM":
    RETURN SOFT_WARN
    flag = "HIGH_FEATURE_RATIO_MEDIUM_DATASET"

# STEP 3: Multicollinearity check
vif_scores = compute_vif(feature_snapshot)

FOR each feature in feature_snapshot:
    IF vif_scores[feature] > 10.0:
        IF risk_tier == TIER_1:
            RETURN HARD_STOP
            reason = f"Feature {feature} VIF={vif_scores[feature]:.1f} exceeds Tier 1 limit of 10."
        ELSE:
            RETURN SOFT_WARN
            flag = f"HIGH_VIF_{feature}"
            # Flag but allow: tree models tolerate collinearity

# STEP 4: Primary selection method routing by dataset size and model family
IF dataset_size == "VERY_SMALL":
    primary_method = VARIANCE_THRESHOLD_THEN_EXPERT_REVIEW
    # No automated selection: not enough data for reliable filter
    RETURN SOFT_WARN
    flag = "VERY_SMALL_DATASET_MANUAL_SELECTION_RECOMMENDED"
    max_features = min(n_rows // 10, n_features)

ELIF dataset_size == "SMALL":
    primary_method = STABILITY_SELECTION_BOOTSTRAP
    n_bootstrap_iterations = 100
    selection_threshold = 0.6  # feature must appear in >60% of bootstrap samples
    max_features = min(n_rows // 20, n_features)

ELIF dataset_size == "MEDIUM":
    IF interpretability_tier == 1:
        primary_method = SHAP_BASED_SELECTION
        max_features = 25  # Hard cap for Tier 1 interpretability
    ELSE:
        primary_method = MUTUAL_INFORMATION_THEN_VIF_PRUNE
        max_features = 50

ELIF dataset_size in ["LARGE", "EXTREME"]:
    IF interpretability_tier == 1:
        primary_method = EMBEDDED_SELECTION_WITH_SHAP_PRUNE
        max_features = 30
    ELIF interpretability_tier == 2:
        primary_method = EMBEDDED_SELECTION
        max_features = 100
    ELSE:
        primary_method = EMBEDDED_SELECTION
        max_features = 200

# STEP 5: Interpretability hard cap enforcement
IF interpretability_tier == 1 AND selected_features.count > 30:
    RETURN HARD_STOP
    reason = f"Tier 1 interpretability requires <=30 features. Current selection: {selected_features.count}."
    action = "Reduce feature set. Requires ML_LEAD sign-off on final selection."

IF interpretability_tier == 2 AND selected_features.count > 100:
    RETURN SOFT_WARN
    flag = f"FEATURE_COUNT_EXCEEDS_TIER2_GUIDELINE"

# STEP 6: SHAP redundancy elimination
IF primary_method in [SHAP_BASED_SELECTION, EMBEDDED_SELECTION_WITH_SHAP_PRUNE]:
    shap_values = compute_shap_values(feature_snapshot, base_model)
    
    FOR each feature_pair (f1, f2) where shap_correlation(f1, f2) > 0.90:
        DROP feature with lower mean_abs_shap
        log_drop(feature, reason=f"SHAP redundancy with {retained_feature}")

# STEP 7: Regulatory blacklist enforcement
FOR each feature in selected_features:
    IF feature IN regulatory_blacklist:
        # regulatory_blacklist maintained by Compliance, updated quarterly
        DROP_FEATURE(feature)
        RETURN HARD_STOP if risk_tier == TIER_1
        RETURN SOFT_WARN if risk_tier in [TIER_2, TIER_3]

# STEP 8: Dimensionality reduction eligibility
IF n_features > max_features AND reduction_needed:
    IF interpretability_tier == 1:
        RETURN HARD_STOP
        reason = "Dimensionality reduction (PCA/SVD) not eligible for Tier 1 interpretability. Must manually select features."
    
    ELIF interpretability_tier == 2:
        IF dataset_type in [TIME_SERIES, PANEL]:
            route_to = SVD
        ELSE:
            route_to = PCA
        RETURN SOFT_WARN
        flag = "DIMENSIONALITY_REDUCTION_APPLIED"
    
    ELSE: # interpretability_tier == 3
        IF dataset_type == NLP:
            route_to = SVD  # LSA
        ELIF dataset_type == CV:
            route_to = PCA_ON_EMBEDDINGS
        ELSE:
            route_to = PCA

# STEP 9: Feature stability validation (time-series only)
IF dataset_type in [TIME_SERIES, PANEL]:
    FOR each feature in selected_features:
        psi = compute_psi_over_time_windows(feature)
        
        IF psi > 0.25:
            RETURN HARD_STOP if risk_tier == TIER_1
            reason = f"Feature {feature} PSI={psi:.3f} over time windows. Unstable for time-series model."
            RETURN SOFT_WARN if risk_tier in [TIER_2, TIER_3]
```

### Escalation Rules

```
Interpretability cap HARD_STOP → ML_LEAD sign-off required within 3 business days
Regulatory blacklist violation → COMPLIANCE notified immediately, feature removal mandatory
VIF > 10 in Tier 1 → MODEL_RISK review, SLA 48 hours
```

### Failure Handling

```
HARD_STOP: Feature selection pipeline halts. Current selected set frozen pending resolution.
Feature drops: All drops logged with reason, SHAP rank, VIF score, or blacklist reference.
Selection audit: Final selected feature set written to Feature Store with full selection rationale.
```

### Mode-Specific Overrides

```
Startup Mode:
  - Interpretability hard cap: SOFT_WARN for Tier 1 > 30 features (not hard stop)
  - SHAP redundancy: Optional, skip if compute budget limited
  - Stability selection: 50 bootstrap iterations minimum (instead of 100)

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - Regulatory blacklist: Checked automatically against Compliance-maintained list, auto-updated monthly
  - SHAP selection: Required for all Tier 1 models, not optional
  - Feature selection rationale: Full audit log required, stored with model artifact
  - Interpretability hard cap: Enforced strictly, no override path without written MODEL_RISK approval
```

---

## Module 6 — Train/Test Strategy

### Inputs

```
feature_snapshot_id:        Final selected feature snapshot
n_rows:                     Integer
dataset_type:               TABULAR | TIME_SERIES | PANEL
target_column:              Name of prediction target
target_type:                BINARY | MULTICLASS | REGRESSION | SURVIVAL
class_distribution:         {class_label: proportion} for classification
has_groups:                 Boolean (e.g., customer ID groups that must not be split)
group_column:               Column name if has_groups == True
has_temporal_order:         Boolean
temporal_column:            Column name if has_temporal_order == True
risk_tier:                  TIER_1 | TIER_2 | TIER_3
domain:                     BANKING | HEALTHCARE | INSURANCE | GENERAL
regulatory_mode:             STANDARD | REGULATED | GDPR_STRICT
```

### Decision Logic

```python
# STEP 1: Dataset size classification
IF n_rows < 200:
    dataset_size = "TINY"
ELIF n_rows < 1000:
    dataset_size = "VERY_SMALL"
ELIF n_rows < 10000:
    dataset_size = "SMALL"
ELIF n_rows < 100000:
    dataset_size = "MEDIUM"
ELSE:
    dataset_size = "LARGE"

# STEP 2: Tiny dataset gate
IF dataset_size == "TINY":
    RETURN HARD_STOP
    reason = f"Dataset has {n_rows} rows. Minimum viable for any ML model is 200 rows. Statistical significance not achievable."

# STEP 3: Temporal ordering check — overrides all other split strategies
IF has_temporal_order == True OR dataset_type in [TIME_SERIES, PANEL]:
    
    IF temporal_column IS NULL:
        RETURN HARD_STOP
        reason = "Temporal dataset detected but temporal_column not defined."
    
    # Validate monotonicity
    IF NOT is_monotonically_sorted(temporal_column):
        RETURN HARD_STOP
        reason = "Temporal column is not monotonically increasing. Sort dataset before splitting."
    
    # Temporal split strategy
    IF dataset_size == "VERY_SMALL":
        strategy = EXPANDING_WINDOW_CV
        n_folds = 3
        min_train_size = 0.5 * n_rows
    
    ELIF dataset_size == "SMALL":
        strategy = ROLLING_WINDOW_CV
        n_folds = 5
        window_size = 0.20 * n_rows
        step_size = 0.10 * n_rows
    
    ELSE: # MEDIUM or LARGE
        strategy = TEMPORAL_HOLD_OUT_WITH_GAP
        train_pct = 0.70
        gap_pct = 0.05  # temporal gap to prevent leakage
        validation_pct = 0.10
        test_pct = 0.15
        
        IF domain == BANKING:
            gap_days = 30  # 30-day gap between train and test
        ELIF domain == HEALTHCARE:
            gap_days = 90
        ELSE:
            gap_days = 14
    
    # Out-of-time validation for regulated mode
    IF regulatory_mode == REGULATED:
        require_oot_validation = True
        oot_period = LATEST_20PCT_OF_TIMELINE
        # OOT set is withheld from all training and standard validation
        # IMV runs separately on OOT set

# STEP 4: Group-based split (overrides random split if groups exist)
ELIF has_groups == True:
    IF group_column IS NULL:
        RETURN HARD_STOP
        reason = "has_groups=True but group_column not defined."
    
    unique_groups = count_unique(group_column)
    
    IF unique_groups < 10:
        RETURN HARD_STOP
        reason = f"Only {unique_groups} unique groups. Stratified group split not statistically viable."
    
    strategy = GROUP_STRATIFIED_SPLIT
    test_pct = 0.20
    
    IF dataset_size in ["VERY_SMALL", "SMALL"]:
        strategy = GROUP_STRATIFIED_CV
        n_folds = 5

# STEP 5: Standard classification/regression split
ELSE:
    IF dataset_size == "VERY_SMALL":
        strategy = BOOTSTRAP_VALIDATION
        n_bootstrap = 200
        RETURN SOFT_WARN
        flag = "VERY_SMALL_DATASET_BOOTSTRAP_VALIDATION"
    
    ELIF dataset_size == "SMALL":
        IF target_type in [BINARY, MULTICLASS]:
            strategy = STRATIFIED_CV
            n_folds = 10
        ELSE:
            strategy = CV
            n_folds = 10
    
    ELIF dataset_size == "MEDIUM":
        strategy = STRATIFIED_TRAIN_VAL_TEST
        train_pct = 0.70
        val_pct = 0.15
        test_pct = 0.15
    
    ELSE: # LARGE
        strategy = STRATIFIED_TRAIN_VAL_TEST
        train_pct = 0.80
        val_pct = 0.10
        test_pct = 0.10

# STEP 6: Stratification check for imbalanced classification
IF target_type in [BINARY, MULTICLASS]:
    minority_class_pct = min(class_distribution.values())
    
    IF minority_class_pct < 0.05:
        IF strategy in [BOOTSTRAP_VALIDATION, CV, STRATIFIED_CV]:
            # Already stratified or bootstrap — flag but don't change
            RETURN SOFT_WARN
            flag = f"SEVERE_IMBALANCE_{minority_class_pct*100:.1f}PCT_MINORITY"
        ELSE:
            enforce_stratification = True
    
    IF minority_class_pct < 0.01:
        RETURN HARD_STOP
        reason = f"Minority class at {minority_class_pct*100:.2f}%. Standard metrics unreliable. Use PR-AUC, not ROC-AUC. Module 8 Imbalance Handling required first."

# STEP 7: Minimum test set size enforcement
IF strategy in [STRATIFIED_TRAIN_VAL_TEST, TEMPORAL_HOLD_OUT_WITH_GAP, GROUP_STRATIFIED_SPLIT]:
    test_n = test_pct * n_rows
    
    IF target_type == BINARY:
        minority_count_in_test = test_n * minority_class_pct
        IF minority_count_in_test < 50:
            RETURN HARD_STOP
            reason = f"Test set has only {minority_count_in_test:.0f} minority class samples. Minimum 50 required for statistical reliability."

# STEP 8: Nested CV for hyperparameter optimization
IF risk_tier == TIER_1 AND strategy in [STRATIFIED_CV, ROLLING_WINDOW_CV]:
    nested_cv = True
    outer_folds = 5
    inner_folds = 3
    # Prevents optimistic bias in hyperparameter selection

# STEP 9: Reproducibility lock
random_seed = 42  # Fixed. Never generated at runtime.
log_split_specification(
    strategy, split_params, random_seed, temporal_column,
    group_column, stratify_column, oot_period
)
```

### Escalation Rules

```
HARD_STOP on tiny dataset → escalate to DATA_ENGINEERING for data acquisition assessment
HARD_STOP on insufficient minority class in test → escalate to ML_LEAD + MODEL_RISK
Temporal monotonicity failure → escalate to DATA_ENGINEERING, SLA 24 hours
```

### Failure Handling

```
HARD_STOP: No split produced. Training cannot proceed.
SOFT_WARN: Split proceeds with flag logged to model card.
Split specification: Fully logged including all parameters and random seed. Reproducible.
OOT set: Locked and inaccessible to ML Engineering until IMV accesses independently.
```

### Mode-Specific Overrides

```
Startup Mode:
  - Nested CV: Optional for Tier 1
  - OOT validation: Optional for REGULATED mode on Tier 2/3
  - Minimum test minority count: Warn at 30, hard stop at 10

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - OOT validation: REQUIRED for all Tier 1 models
  - Nested CV: REQUIRED for all Tier 1 models using hyperparameter search
  - Split specification: Must be written to audit log before any training begins
  - Random seed: Must be logged to model registry before training
```

---

## Module 7 — Model Family Selection

### Inputs

```
interpretability_tier:      1 | 2 | 3 (from Business Decision Charter)
risk_tier:                  TIER_1 | TIER_2 | TIER_3
dataset_size:               TINY | VERY_SMALL | SMALL | MEDIUM | LARGE | EXTREME
dataset_type:               TABULAR | TIME_SERIES | PANEL | NLP | CV | GRAPH
target_type:                BINARY | MULTICLASS | REGRESSION | SURVIVAL | RANKING
domain:                     BANKING | HEALTHCARE | INSURANCE | GENERAL
has_monotonic_constraints:  Boolean (from Business Decision Charter)
requires_probability:       Boolean
requires_explanation:       Boolean
n_features:                 Integer (final selected feature count)
regulatory_mode:             STANDARD | REGULATED | GDPR_STRICT
```

### Decision Logic

```python
# STEP 1: Interpretability gate — hardest constraint, evaluated first
IF interpretability_tier == 1:
    eligible_families = [
        LOGISTIC_REGRESSION,
        DECISION_TREE_SHALLOW,  # max_depth <= 5
        LINEAR_REGRESSION,
        SCORECARD_MODEL,        # banking-specific
        RIDGE_REGRESSION,
        LASSO_REGRESSION
    ]
    # All other families: HARD BLOCK regardless of performance
    
    IF risk_tier == TIER_1 AND regulatory_mode == REGULATED:
        eligible_families = [
            LOGISTIC_REGRESSION,
            SCORECARD_MODEL,
            LINEAR_REGRESSION
        ]
        # Shallow decision trees removed in fully regulated Tier 1

ELIF interpretability_tier == 2:
    eligible_families = [
        LOGISTIC_REGRESSION,
        DECISION_TREE_SHALLOW,
        RANDOM_FOREST,
        GRADIENT_BOOSTING_XGB,
        GRADIENT_BOOSTING_LGBM,
        LINEAR_SVM,
        LINEAR_REGRESSION,
        RIDGE_REGRESSION,
        ELASTIC_NET,
        SURVIVAL_MODEL,          # if target_type == SURVIVAL
        ARIMA_FAMILY             # if dataset_type == TIME_SERIES
    ]
    # Requires full SHAP explanation coverage for any non-linear family

ELSE: # interpretability_tier == 3
    eligible_families = [
        ALL_ABOVE,
        NEURAL_NETWORK_SHALLOW,  # <= 3 layers, <= 256 units
        ENSEMBLE_STACKED,
        DEEP_LEARNING_TABNET,
        TRANSFORMER_TABULAR,
        PROPHET,                  # time-series
        LSTM                      # time-series, if justified
    ]

# STEP 2: Dataset type routing within eligible families
IF dataset_type == TIME_SERIES:
    time_series_eligible = [
        ARIMA, SARIMA, ETS,         # statistical baselines always eligible
        GRADIENT_BOOSTING_WITH_LAGS,
        LSTM if interpretability_tier == 3,
        PROPHET if interpretability_tier in [2, 3]
    ]
    eligible_families = intersect(eligible_families, time_series_eligible)
    
    IF eligible_families IS EMPTY:
        RETURN HARD_STOP
        reason = "No eligible model family for TIME_SERIES given interpretability constraints."

ELIF dataset_type == NLP:
    IF interpretability_tier == 1:
        RETURN HARD_STOP
        reason = "NLP models cannot satisfy Tier 1 interpretability requirements. Use structured features."
    eligible_families = [TF_IDF_THEN_LOGISTIC, FASTTEXT] if interpretability_tier == 2
    eligible_families = [FINE_TUNED_TRANSFORMER] if interpretability_tier == 3

ELIF dataset_type == CV:
    IF interpretability_tier in [1, 2]:
        RETURN HARD_STOP
        reason = "Computer vision models cannot satisfy Tier 1 or 2 interpretability requirements."
    eligible_families = [CNN, RESNET, VIT] if interpretability_tier == 3

# STEP 3: Dataset size routing
IF dataset_size == "VERY_SMALL":
    REMOVE_FROM_ELIGIBLE [NEURAL_NETWORK_SHALLOW, DEEP_LEARNING_TABNET, RANDOM_FOREST, GRADIENT_BOOSTING_XGB, GRADIENT_BOOSTING_LGBM, LSTM]
    # Small data: complex models overfit severely
    IF eligible_families IS EMPTY OR only_complex_families_remain:
        RETURN HARD_STOP
        reason = "No appropriate model family for VERY_SMALL dataset with current interpretability tier."

ELIF dataset_size == "SMALL":
    REMOVE_FROM_ELIGIBLE [LSTM, DEEP_LEARNING_TABNET, TRANSFORMER_TABULAR]
    PREFER [LOGISTIC_REGRESSION, RIDGE_REGRESSION, DECISION_TREE_SHALLOW]

ELIF dataset_size in ["LARGE", "EXTREME"]:
    # All eligible families remain, routing to efficient implementations
    IF GRADIENT_BOOSTING_XGB in eligible_families:
        set framework = LIGHTGBM  # More memory efficient at scale
    IF RANDOM_FOREST in eligible_families:
        set n_estimators_max = 500  # Cap for inference latency

# STEP 4: Monotonic constraint enforcement
IF has_monotonic_constraints == True:
    REMOVE_FROM_ELIGIBLE [RANDOM_FOREST, NEURAL_NETWORK_SHALLOW, DEEP_LEARNING_TABNET]
    # These families cannot natively enforce monotonicity
    IF GRADIENT_BOOSTING_XGB in eligible_families:
        set enforce_monotonic_constraints = True
    IF LOGISTIC_REGRESSION in eligible_families:
        set feature_signs_defined = True  # Coefficient signs must match constraint direction

# STEP 5: Probability calibration requirement
IF requires_probability == True:
    REMOVE_FROM_ELIGIBLE [LINEAR_SVM]
    # SVM does not produce native probabilities reliably
    FOR each family in eligible_families using GRADIENT_BOOSTING OR RANDOM_FOREST:
        set requires_calibration = True
        set calibration_method = ISOTONIC if n_rows > 1000 else PLATT_SCALING

# STEP 6: Domain-specific routing
IF domain == BANKING:
    IF target_type == BINARY AND interpretability_tier in [1, 2]:
        PREFER SCORECARD_MODEL THEN LOGISTIC_REGRESSION
        # Regulatory preference: scorecards are auditable by regulators
    
    IF has_survival_analysis_target:
        eligible_families = [COX_PROPORTIONAL_HAZARDS, ACCELERATED_FAILURE_TIME]

IF domain == HEALTHCARE:
    IF interpretability_tier == 1:
        PREFER LOGISTIC_REGRESSION
        # Clinical interpretability: odds ratios must be meaningful
    IF target_type == SURVIVAL:
        PREFER COX_PROPORTIONAL_HAZARDS

# STEP 7: Final selection and baseline requirement
IF eligible_families IS EMPTY:
    RETURN HARD_STOP
    reason = "No eligible model family satisfies all constraints. Review interpretability tier or dataset requirements."

# Baseline model always required
baseline_model = LOGISTIC_REGRESSION if target_type in [BINARY, MULTICLASS]
baseline_model = LINEAR_REGRESSION if target_type == REGRESSION
baseline_model = NAIVE_FORECAST if dataset_type == TIME_SERIES
# Candidate models must beat baseline or they are not promoted

# Maximum candidate models
max_candidates = 3 if risk_tier == TIER_1 else 5

# Log final eligible set
log_model_family_selection(eligible_families, rationale, constraints_applied)
```

### Escalation Rules

```
Empty eligible family set → escalate to ML_LEAD + MODEL_RISK, SLA 3 business days for constraint review
NLP/CV Tier 1 interpretability conflict → escalate to MODEL_RISK for use case scope revision
```

### Failure Handling

```
HARD_STOP: No model family assigned. Training cannot start.
Constraint logging: All applied constraints logged to model card with rationale.
Removed families: Logged with reason (interpretability block, size constraint, etc.)
```

### Mode-Specific Overrides

```
Startup Mode:
  - Baseline model: Optional but strongly recommended
  - Max candidates: 5 regardless of tier

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - Scorecard model: Required evaluation for all BANKING TIER_1 BINARY models
  - Interpretability tier 1 cap: Strictly enforced, no override
  - Candidate model list: Must be approved in writing before training
  - Black-box families in Tier 1: Absolutely prohibited
```

---

## Module 8 — Imbalance Handling

### Inputs

```
class_distribution:         {class_label: proportion}
n_rows:                     Integer
n_minority_class:           Integer count of minority class samples
target_type:                BINARY | MULTICLASS
dataset_size:               TINY | VERY_SMALL | SMALL | MEDIUM | LARGE | EXTREME
model_family:               Selected model family from Module 7
risk_tier:                  TIER_1 | TIER_2 | TIER_3
domain:                     BANKING | HEALTHCARE | INSURANCE | GENERAL
business_cost_matrix:       {FP_cost: float, FN_cost: float} from Business Decision Charter
regulatory_mode:             STANDARD | REGULATED | GDPR_STRICT
```

### Decision Logic

```python
# STEP 1: Imbalance severity classification
minority_pct = min(class_distribution.values())

IF minority_pct >= 0.30:
    imbalance_severity = "NONE"
    strategy = NO_RESAMPLING
    # No imbalance action needed

ELIF minority_pct >= 0.15:
    imbalance_severity = "MILD"
    strategy = CLASS_WEIGHT_ONLY

ELIF minority_pct >= 0.05:
    imbalance_severity = "MODERATE"
    # Route by dataset size

ELIF minority_pct >= 0.01:
    imbalance_severity = "SEVERE"

ELIF minority_pct >= 0.001:
    imbalance_severity = "EXTREME"

ELSE:
    imbalance_severity = "PATHOLOGICAL"
    RETURN HARD_STOP
    reason = f"Minority class at {minority_pct*100:.3f}%. Minority class has fewer than 1-in-1000 samples. ML model not viable."

# STEP 2: Strategy routing by severity and dataset size
IF imbalance_severity == "MILD":
    strategy = CLASS_WEIGHT_BALANCING
    class_weight_ratio = compute_class_weight(class_distribution)

ELIF imbalance_severity == "MODERATE":
    IF dataset_size in ["VERY_SMALL", "SMALL"]:
        strategy = SMOTE
        # Generates synthetic minority samples
        k_neighbors = min(5, n_minority_class - 1)
        IF k_neighbors < 2:
            strategy = CLASS_WEIGHT_BALANCING
            RETURN SOFT_WARN
            flag = "TOO_FEW_MINORITY_SAMPLES_FOR_SMOTE"
    
    ELIF dataset_size in ["MEDIUM", "LARGE", "EXTREME"]:
        IF model_family in [GRADIENT_BOOSTING_XGB, GRADIENT_BOOSTING_LGBM]:
            strategy = SCALE_POS_WEIGHT_PARAMETER
            # Built-in, no resampling needed
        ELIF model_family == LOGISTIC_REGRESSION:
            strategy = CLASS_WEIGHT_BALANCING
        ELSE:
            strategy = RANDOM_UNDERSAMPLING_MAJORITY
            undersample_ratio = 0.1  # Cap majority class at 10x minority

ELIF imbalance_severity == "SEVERE":
    IF n_minority_class < 50:
        RETURN HARD_STOP
        reason = f"Only {n_minority_class} minority class samples. Cannot train reliable model."
    
    IF dataset_size in ["VERY_SMALL", "SMALL"]:
        RETURN HARD_STOP
        reason = f"Severe imbalance ({minority_pct*100:.2f}%) with small dataset. Not viable."
    
    IF model_family in [GRADIENT_BOOSTING_XGB, GRADIENT_BOOSTING_LGBM]:
        strategy = SCALE_POS_WEIGHT_PARAMETER
    ELIF model_family == RANDOM_FOREST:
        strategy = [CLASS_WEIGHT_BALANCING, SMOTEENN]
        # SMOTEENN: combines SMOTE with Edited Nearest Neighbors cleaning
    ELSE:
        strategy = [ADASYN, RANDOM_UNDERSAMPLING_MAJORITY]

ELIF imbalance_severity == "EXTREME":
    IF n_minority_class < 100:
        RETURN HARD_STOP
        reason = f"Only {n_minority_class} minority samples with extreme imbalance. Model not viable."
    
    RETURN SOFT_WARN
    flag = "EXTREME_IMBALANCE_CONSIDER_ANOMALY_DETECTION"
    
    # Anomaly detection routing check
    IF business_objective == "FRAUD_DETECTION" OR domain_flag == "OUTLIER_DETECTION":
        RECOMMEND route_to = ISOLATION_FOREST OR AUTOENCODERS
        # Standard classification not recommended
    ELSE:
        strategy = [ADASYN, CLUSTER_CENTROIDS_UNDERSAMPLING]

# STEP 3: Cost-sensitive learning check
IF business_cost_matrix IS NOT NULL:
    FP_cost = business_cost_matrix.FP_cost
    FN_cost = business_cost_matrix.FN_cost
    cost_ratio = FN_cost / FP_cost
    
    IF cost_ratio > 5.0:
        # Missed positives far more costly than false alarms
        override_strategy = COST_SENSITIVE_LEARNING
        set class_weight = {positive: cost_ratio, negative: 1.0}
        RETURN SOFT_WARN
        flag = f"COST_RATIO_{cost_ratio:.1f}_OVERRIDES_RESAMPLING"
        strategy = COST_SENSITIVE_LEARNING
    
    IF cost_ratio < 0.5:
        # False positives more costly than missed positives
        override_strategy = COST_SENSITIVE_LEARNING
        set class_weight = {positive: 1.0, negative: 1.0 / cost_ratio}
        strategy = COST_SENSITIVE_LEARNING

# STEP 4: Domain-specific overrides
IF domain == HEALTHCARE:
    IF target_column == "MORTALITY" OR target_column == "ADVERSE_EVENT":
        # Missing a true positive (missed mortality) catastrophically costly
        IF FN_cost IS NULL:
            RETURN HARD_STOP
            reason = "Healthcare mortality/adverse event model requires explicit FN cost in Business Decision Charter."
        enforce_minimum_recall = True
        minimum_recall_threshold = 0.85
        # Threshold will be set in Module 9 to achieve this recall

IF domain == BANKING AND target_column in ["DEFAULT", "FRAUD"]:
    IF strategy == SMOTE:
        RETURN SOFT_WARN
        flag = "SMOTE_ON_FINANCIAL_DATA_REVIEW_REQUIRED"
        # Synthetic financial samples may not represent real fraud patterns
        # Recommend class weight or scale_pos_weight instead

# STEP 5: Validation set preservation
IF strategy in [SMOTE, ADASYN, SMOTEENN]:
    enforce_resampling_train_only = True
    # CRITICAL: Resampling applied ONLY to training set
    # Validation and test sets use original distribution
    IF this_constraint_violated:
        RETURN HARD_STOP
        reason = "Resampling applied to validation or test set. This creates optimistic bias. Pipeline halted."

# STEP 6: Metric routing consequence
IF imbalance_severity in ["SEVERE", "EXTREME"]:
    set primary_metric = PR_AUC
    set secondary_metric = F1_SCORE
    PROHIBIT primary_metric = ROC_AUC
    PROHIBIT primary_metric = ACCURACY
    
    RETURN SOFT_WARN
    flag = "ROC_AUC_UNRELIABLE_AT_SEVERE_IMBALANCE_USE_PR_AUC"
```

### Escalation Rules

```
HARD_STOP on insufficient minority samples → escalate to DATA_ENGINEERING for data acquisition
HARD_STOP on pathological imbalance → escalate to ML_LEAD for use case viability review
SMOTE on banking financial data → ML_LEAD review before proceeding
```

### Failure Handling

```
HARD_STOP: Imbalance strategy unresolvable. Training cannot proceed.
Strategy log: Chosen strategy logged with rationale, minority count, cost matrix reference.
Resampling audit: Before/after class distributions logged for model card.
```

### Mode-Specific Overrides

```
Startup Mode:
  - Pathological threshold: Warn at 0.0005 (not hard stop) with documentation
  - SMOTE validation contamination: Warn-only (treat as soft error)

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - SMOTE on Tier 1 models: Requires MODEL_RISK written sign-off
  - Cost matrix: REQUIRED for all Tier 1 regulated models, HARD_STOP if absent
  - Resampling validation contamination: HARD_STOP, no exceptions
  - PR-AUC required for severe/extreme imbalance: Enforced, no override
```

---

## Module 9 — Threshold Optimization

### Inputs

```
model_artifact_id:          Trained model artifact from Model Lifecycle
calibrated_probabilities:   Probability outputs on validation set (post-calibration)
true_labels:                Ground truth labels for validation set
business_cost_matrix:       {FP_cost, FN_cost, TP_value, TN_value}
target_type:                BINARY | MULTICLASS | REGRESSION
risk_tier:                  TIER_1 | TIER_2 | TIER_3
domain:                     BANKING | HEALTHCARE | INSURANCE | GENERAL
has_regulatory_constraint:  Boolean
regulatory_min_recall:      Float (if domain constraint applies)
regulatory_max_fpr:         Float (if domain constraint applies)
deployment_mode:            AUTOMATED | HUMAN_REVIEWED | HYBRID
imbalance_severity:         from Module 8
n_validation_samples:       Integer
fallback_trigger_level:     Float (confidence below which human escalation triggers)
regulatory_mode:             STANDARD | REGULATED | GDPR_STRICT
```

### Decision Logic

```python
# STEP 1: Calibration check before thresholding
calibration_error = compute_expected_calibration_error(calibrated_probabilities, true_labels)

IF calibration_error > 0.05:
    IF risk_tier == TIER_1:
        RETURN HARD_STOP
        reason = f"Calibration error {calibration_error:.3f} exceeds Tier 1 limit of 0.05. Recalibrate before threshold optimization."
    ELSE:
        RETURN SOFT_WARN
        flag = f"CALIBRATION_ERROR_{calibration_error:.3f}"

# STEP 2: Minimum validation set size for reliable threshold
IF target_type == BINARY:
    minority_count_in_val = sum(true_labels == minority_class)
    IF minority_count_in_val < 50:
        RETURN HARD_STOP
        reason = f"Only {minority_count_in_val} minority class samples in validation set. Threshold optimization unreliable."

# STEP 3: Select threshold optimization objective
IF business_cost_matrix IS NOT NULL:
    FP_cost = business_cost_matrix.FP_cost
    FN_cost = business_cost_matrix.FN_cost
    
    IF FP_cost <= 0 OR FN_cost <= 0:
        RETURN HARD_STOP
        reason = "Cost matrix contains zero or negative costs. Business Decision Charter must be corrected."
    
    optimization_objective = MINIMIZE_EXPECTED_COST
    # Expected cost = FP_cost * FP_rate * n + FN_cost * FN_rate * n
    
    threshold_search_space = linspace(0.01, 0.99, 990)
    optimal_threshold = argmin(expected_cost, over=threshold_search_space)

ELIF has_regulatory_constraint == True:
    IF regulatory_min_recall IS NOT NULL:
        # Find minimum threshold that achieves required recall
        # Then among all thresholds meeting recall constraint, pick highest precision
        candidates = [t for t in threshold_search_space where recall(t) >= regulatory_min_recall]
        IF candidates IS EMPTY:
            RETURN HARD_STOP
            reason = f"Model cannot achieve required recall {regulatory_min_recall} at any threshold. Model fails regulatory constraint."
        optimal_threshold = max(candidates, key=precision)
    
    ELIF regulatory_max_fpr IS NOT NULL:
        candidates = [t for t in threshold_search_space where fpr(t) <= regulatory_max_fpr]
        IF candidates IS EMPTY:
            RETURN HARD_STOP
            reason = f"Model cannot satisfy max FPR constraint of {regulatory_max_fpr}."
        optimal_threshold = max(candidates, key=recall)

ELSE:
    # No cost matrix, no regulatory constraint
    IF imbalance_severity in ["SEVERE", "EXTREME"]:
        optimization_objective = MAXIMIZE_F1
    ELSE:
        optimization_objective = MAXIMIZE_J_STATISTIC  # Youden's J = sensitivity + specificity - 1
    
    optimal_threshold = compute_optimal_threshold(optimization_objective, calibrated_probabilities, true_labels)

# STEP 4: Domain-specific threshold floor and ceiling
IF domain == HEALTHCARE AND target_column in ["MORTALITY", "ADVERSE_EVENT", "SEPSIS"]:
    minimum_recall_floor = 0.85
    IF recall_at_optimal_threshold < minimum_recall_floor:
        # Override to floor
        threshold_at_recall_floor = find_threshold_for_recall(minimum_recall_floor)
        optimal_threshold = threshold_at_recall_floor
        RETURN SOFT_WARN
        flag = f"THRESHOLD_OVERRIDDEN_TO_RECALL_FLOOR_{minimum_recall_floor}"

IF domain == BANKING AND target_column == "FRAUD":
    minimum_recall_floor = 0.75
    IF recall_at_optimal_threshold < minimum_recall_floor:
        threshold_at_recall_floor = find_threshold_for_recall(minimum_recall_floor)
        optimal_threshold = threshold_at_recall_floor
        RETURN SOFT_WARN
        flag = "THRESHOLD_OVERRIDDEN_TO_BANKING_FRAUD_RECALL_FLOOR"

IF domain == BANKING AND target_column == "DEFAULT":
    # PD models: conservative threshold, avoid over-predicting non-default
    maximum_fpr_ceiling = 0.20
    IF fpr_at_optimal_threshold > maximum_fpr_ceiling:
        RETURN SOFT_WARN
        flag = "FPR_EXCEEDS_BANKING_DEFAULT_CEILING"

# STEP 5: Fallback trigger threshold definition
IF deployment_mode == HYBRID:
    # Confidence below this level → human escalation queue
    IF fallback_trigger_level IS NULL:
        fallback_trigger_level = compute_fallback_trigger(calibrated_probabilities)
        # Default: 10th percentile of confidence distribution on validation set
        # Approximately 10% of borderline decisions routed to human
    
    IF fallback_trigger_level >= optimal_threshold:
        RETURN HARD_STOP
        reason = "Fallback trigger level cannot be >= deployment threshold. All decisions would escalate."

IF deployment_mode == AUTOMATED AND risk_tier == TIER_1:
    IF regulatory_mode == REGULATED:
        require_fallback_definition = True
        IF fallback_trigger_level IS NULL:
            RETURN HARD_STOP
            reason = "Regulated Tier 1 automated deployment requires defined fallback trigger level."

# STEP 6: Lock threshold in model registry
locked_threshold = {
    optimal_threshold: optimal_threshold,
    fallback_trigger_level: fallback_trigger_level,
    optimization_objective: optimization_objective,
    cost_matrix_reference: business_cost_matrix_id,
    validation_metrics_at_threshold: {
        precision, recall, fpr, f1, expected_cost
    },
    business_owner_sign_off_required: True,
    locked_by: "MODULE_9_SERVICE",
    lock_timestamp: now()
}
write_to_model_registry(model_artifact_id, locked_threshold)

IF business_owner_sign_off_required:
    notify(business_model_owner, "Threshold requires your written sign-off before deployment approval.")
    # Deployment cannot proceed until business_owner signs threshold document

# STEP 7: Multiclass extension
IF target_type == MULTICLASS:
    FOR each class_c in classes:
        compute class_specific_threshold using OVR_strategy
        optimize using class_c_cost if available else MAXIMIZE_F1_MACRO
    lock_per_class_thresholds_to_registry(model_artifact_id)
```

### Escalation Rules

```
Regulatory constraint not achievable → escalate to MODEL_RISK + BUSINESS_OWNER, SLA 5 business days
Calibration error HARD_STOP → back to training, calibration method must change
Business owner threshold sign-off > 5 business days → escalate to ML_LEAD
```

### Failure Handling

```
HARD_STOP: Threshold not set. Model cannot be submitted for approval.
Threshold log: All evaluated thresholds and their metric profiles logged.
Cost matrix reference: Locked in registry alongside threshold. Cannot be changed post-lock without re-running Module 9.
```

### Mode-Specific Overrides

```
Startup Mode:
  - Business owner sign-off: Asynchronous, not blocking deployment
  - Calibration check: SOFT_WARN only for Tier 1

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - Business owner sign-off: BLOCKING. Deployment blocked until signed.
  - Fallback trigger level: REQUIRED for all Tier 1 models
  - Threshold lock: Immutable post-approval. Any change requires full Module 9 rerun + re-approval.
  - Threshold justification document: Auto-generated and stored with model card
```

---

## Module 10 — Drift Handling

### Inputs

```
model_artifact_id:          Deployed model in production
champion_deployment_date:   ISO timestamp of production deployment
feature_distributions_train: Baseline feature distributions from training set
prediction_distribution_train: Baseline score distribution from training set
current_feature_distributions: Rolling 30-day feature distributions from Audit Log
current_prediction_distribution: Rolling 30-day score distribution from Audit Log
outcome_labels:              Actual outcome labels (where available, with lag)
psi_thresholds:              {yellow: float, red: float}
ks_threshold:                Float
fairness_baseline:           Disparate impact ratios at deployment from Module 9
fairness_current:             Current disparate impact ratios from Audit Log
risk_tier:                  TIER_1 | TIER_2 | TIER_3
domain:                     BANKING | HEALTHCARE | INSURANCE | GENERAL
regulatory_mode:             STANDARD | REGULATED | GDPR_STRICT
auto_retrain_eligible:       Boolean (from Business Decision Charter)
```

### Decision Logic

```python
# PSI default thresholds (customizable per use case in Business Decision Charter)
PSI_YELLOW = 0.10
PSI_RED = 0.20
KS_THRESHOLD = 0.10  # p-value threshold for KS test significance
FAIRNESS_DI_LOWER = 0.80  # Disparate impact ratio lower bound

# STEP 1: Per-feature PSI computation (daily scheduled job)
FOR each feature in deployed_model.features:
    psi = compute_psi(feature_distributions_train[feature], current_feature_distributions[feature])
    
    IF psi < PSI_YELLOW:
        status = "STABLE"
        log_drift_status(feature, psi, "STABLE")
    
    ELIF psi < PSI_RED:
        status = "YELLOW"
        log_drift_status(feature, psi, "YELLOW")
        increment_yellow_count(feature)
        
        IF yellow_count_consecutive_days(feature) >= 7:
            # Sustained yellow for 7 days → escalate
            trigger_incident(level=1, feature=feature, psi=psi)
    
    ELSE: # psi >= PSI_RED
        status = "RED"
        log_drift_status(feature, psi, "RED")
        trigger_incident(level=2, feature=feature, psi=psi)

# Count of features in RED state
red_feature_count = count(feature for feature in features where psi >= PSI_RED)
total_features = count(features)

IF red_feature_count / total_features > 0.20:
    # >20% of features in RED state
    trigger_incident(level=3, reason="SYSTEMIC_FEATURE_DRIFT")

# STEP 2: Score distribution drift (daily scheduled job)
score_psi = compute_psi(prediction_distribution_train, current_prediction_distribution)

IF score_psi >= PSI_RED:
    trigger_incident(level=2, reason=f"SCORE_DISTRIBUTION_DRIFT_PSI={score_psi:.3f}")

IF score_psi >= 0.30:
    trigger_incident(level=3, reason=f"SEVERE_SCORE_DRIFT_PSI={score_psi:.3f}")

# STEP 3: KS test on feature distributions (weekly scheduled job)
FOR each feature in deployed_model.features:
    ks_stat, ks_pvalue = compute_ks_test(feature_distributions_train[feature], current_feature_distributions[feature])
    
    IF ks_pvalue < KS_THRESHOLD:
        RETURN SOFT_WARN
        flag = f"KS_DRIFT_DETECTED_{feature}_pvalue={ks_pvalue:.4f}"
        
        IF ks_stat > 0.30:
            trigger_incident(level=2, reason=f"KS_SEVERE_DRIFT_{feature}")

# STEP 4: Fairness monitoring (weekly scheduled job)
FOR each protected_attribute in fairness_baseline:
    current_di = compute_disparate_impact(
        decisions = audit_log.decisions_last_30_days,
        protected_attr = protected_attribute
    )
    
    IF current_di < FAIRNESS_DI_LOWER:
        trigger_incident(level=3, reason=f"FAIRNESS_THRESHOLD_BREACH_{protected_attribute}_DI={current_di:.3f}")
        # Fairness breach is always Level 3 minimum
        
        IF regulatory_mode == REGULATED:
            trigger_incident(level=3, reason=f"REGULATORY_FAIRNESS_BREACH")
            notify_compliance_immediately = True

# STEP 5: Outcome-based performance monitoring (cadence = label latency window)
IF outcome_labels IS NOT NULL AND outcome_labels.count >= 100:
    
    current_auc = compute_auc(outcome_labels, historical_scores_matching_labels)
    baseline_auc = model_registry.baseline_auc_at_approval
    auc_degradation = (baseline_auc - current_auc) / baseline_auc
    
    IF auc_degradation > 0.10:
        RETURN SOFT_WARN
        flag = f"AUC_DEGRADATION_{auc_degradation*100:.1f}PCT"
    
    IF auc_degradation > 0.20:
        trigger_incident(level=2, reason=f"AUC_SEVERE_DEGRADATION_{auc_degradation*100:.1f}PCT")
    
    IF auc_degradation > 0.30:
        trigger_incident(level=3, reason=f"AUC_CRITICAL_DEGRADATION_MODEL_REPLACEMENT_REQUIRED")

# STEP 6: Incident response routing
FUNCTION trigger_incident(level, reason, feature=None):
    
    IF level == 1:
        notify_channel = MLOPS_MONITORING_CHANNEL
        sla_hours = 4
        action = "INVESTIGATE_AND_DOCUMENT"
        auto_action = None
    
    ELIF level == 2:
        notify_channel = [MLOPS_ONCALL, MODEL_RISK_EMAIL]
        sla_hours = 2
        action = "JOINT_TRIAGE"
        
        # Auto-actions available at Level 2 (Model Risk must authorize):
        available_auto_actions = [
            TIGHTEN_CONFIDENCE_THRESHOLD,    # Increase fallback trigger level by 0.05
            ACTIVATE_CHALLENGER_AS_CHAMPION, # If challenger exists and has passed validation
            ESCALATE_TO_LEVEL_3
        ]
        
        # Threshold tightening auto-logic
        IF action_selected == TIGHTEN_CONFIDENCE_THRESHOLD:
            new_fallback_trigger = current_fallback_trigger + 0.05
            IF new_fallback_trigger > 0.50:
                RETURN HARD_STOP
                reason = "Confidence threshold tightening would route >50% of decisions to fallback. Escalate to Level 3."
            update_fallback_trigger(model_artifact_id, new_fallback_trigger)
            log_action("THRESHOLD_TIGHTENED", authorized_by="MODEL_RISK", timestamp=now())
    
    ELIF level == 3:
        notify_channel = [MLOPS_ONCALL, MODEL_RISK_EMAIL, CRO_OFFICE_ALERT]
        sla_hours = 0.5  # 30 minutes
        action = "INCIDENT_COMMANDER_ASSIGNED"
        
        # Immediate auto-action: suspend champion model
        suspend_champion(model_artifact_id)
        
        IF challenger_model_exists AND challenger.status == DEPLOYED:
            promote_challenger_to_champion(challenger_id)
            log_action("CHALLENGER_EMERGENCY_PROMOTION", timestamp=now())
        ELIF prior_champion_exists:
            restore_prior_champion(prior_champion_id)
            log_action("PRIOR_CHAMPION_RESTORED", timestamp=now())
        ELSE:
            activate_fallback_spec(model_artifact_id)
            log_action("FALLBACK_ACTIVATED_NO_ALTERNATIVE_MODEL", timestamp=now())
        
        # Regulatory notification assessment
        IF regulatory_mode == REGULATED:
            initiate_regulatory_notification_assessment(
                incident_id, reason, affected_population_estimate
            )
            # EU AI Act Art. 62: 15-day notification window starts from incident classification
        
        post_incident_review_sla_days = 5
        schedule_post_incident_review(incident_id, sla=post_incident_review_sla_days)
    
    ELIF level == 4:
        notify_channel = [CRO_IMMEDIATE_PAGE, LEGAL_IMMEDIATE_PAGE, COMPLIANCE_IMMEDIATE_PAGE]
        auto_action = SUSPEND_MODEL_IMMEDIATELY
        suspend_champion(model_artifact_id)
        initiate_regulatory_notification(incident_id)  # No assessment delay at Level 4
        initiate_customer_remediation_assessment(incident_id)

# STEP 7: Retraining trigger routing
IF incident_level >= 2 AND drift_trigger_confirmed:
    
    IF auto_retrain_eligible == False OR risk_tier == TIER_1:
        notify("RETRAINING_TRIGGER_ISSUED")
        notify_target = ["ML_ENGINEERING", "MODEL_RISK"]
        action = "INITIATE_FULL_MODULE_1_TO_9_PIPELINE"
        # No shortcut path for Tier 1
        note = "New model must complete full validation pipeline before replacing champion."
    
    ELIF risk_tier in [TIER_2, TIER_3] AND auto_retrain_eligible == True:
        IF drift_type == "DATA_WINDOW_SHIFT_ONLY":
            # Only training data window changed, no feature or schema changes
            initiate_fast_track_retrain(
                model_artifact_id,
                modules_required = [MODULE_1, MODULE_3, MODULE_7, MODULE_9],
                skip_modules = [MODULE_2, MODULE_4, MODULE_5, MODULE_6, MODULE_8],
                imv_review_sla_days = 5
            )
        ELSE:
            initiate_full_retrain(model_artifact_id)

# STEP 8: Approval expiry check (runs on daily scheduled job)
FOR each deployed_model in model_registry:
    days_since_approval = today - deployed_model.approval_date
    
    IF risk_tier == TIER_1:
        approval_validity_days = 180  # 6 months
    ELSE:
        approval_validity_days = 365  # 12 months
    
    IF days_since_approval >= approval_validity_days - 30:
        RETURN SOFT_WARN
        flag = f"MODEL_APPROVAL_EXPIRY_IN_{approval_validity_days - days_since_approval}_DAYS"
        notify(["MODEL_OWNER", "MODEL_RISK"], message=f"Revalidation required within 30 days.")
    
    IF days_since_approval >= approval_validity_days:
        RETURN HARD_STOP
        reason = "Model approval has expired. Model must be revalidated before continuing in production."
        suspend_model_from_automated_decisions(model_artifact_id)
        # Model can continue in human-reviewed mode pending revalidation
        IF deployment_mode == HUMAN_REVIEWED:
            allow_continued_use_with_flag = True
        ELSE:
            activate_fallback_spec(model_artifact_id)
```

### Escalation Rules

```
Level 1 incident SLA breach (>4 hours) → auto-escalate to Level 2
Level 2 incident SLA breach (>2 hours) → auto-escalate to Level 3
Fairness breach → always Level 3 minimum, Compliance notified immediately
Approval expiry HARD_STOP → MODEL_RISK must assign revalidation team within 24 hours
>20% features in RED state → Level 3 regardless of other signals
```

### Failure Handling

```
HARD_STOP on approval expiry: Model suspended from automated mode. Incident created automatically.
Champion suspension: Logged to audit trail with timestamp, authorized_by field, incident reference.
Post-incident review: Mandatory for Level 3+. Output goes to Model Risk Committee.
All drift scores: Retained in time-series monitoring store for 3 years minimum.
```

### Mode-Specific Overrides

```
Startup Mode:
  - PSI_RED threshold: 0.25 (relaxed from 0.20)
  - Fairness monitoring: Monthly (not weekly)
  - Approval expiry: 24 months for all tiers
  - Level 3 auto-suspension: Requires manual confirmation (not automatic)

Enterprise Mode:
  - All defaults as specified above

Regulated Mode:
  - PSI_RED threshold: 0.15 (tightened from 0.20)
  - Fairness monitoring: Daily for Tier 1 models
  - Regulatory notification assessment: Initiated at Level 2 (not Level 3)
  - Approval expiry: 90 days for Tier 1 high-risk models under EU AI Act
  - Drift log retention: 5 years minimum
  - Post-incident review: External auditor notification required for Level 3+
  - Model suspension: Automatic, no human confirmation required at Level 3
```

---

## Global Failure Mode Summary

| Condition | Default Mode | Regulated Mode | Domain Override |
|---|---|---|---|
| Schema contract missing (Tier 1) | HARD_STOP | HARD_STOP | — |
| Undeclared PII | SOFT_WARN | HARD_STOP | — |
| MI leakage > 0.85 (Tier 1) | HARD_STOP | HARD_STOP | — |
| MNAR feature (Tier 1) | HARD_STOP | HARD_STOP | — |
| Protected attribute in Tier 1 encoding | HARD_STOP | HARD_STOP | — |
| Pathological imbalance | HARD_STOP | HARD_STOP | — |
| Threshold regulatory constraint unachievable | HARD_STOP | HARD_STOP | — |
| Approval expiry | HARD_STOP (auto) | HARD_STOP (auto) | — |
| Level 3 drift incident | Suspend + restore | Suspend + regulatory notify | Fairness always L3 |
| Calibration error > 0.05 (Tier 1) | HARD_STOP | HARD_STOP | — |
| No eligible model family | HARD_STOP | HARD_STOP | — |
| Temporal leakage (Tier 1) | HARD_STOP | HARD_STOP | — |
| PSI RED (single feature) | Incident L2 | Incident L2 (notify Compliance) | — |
| PSI RED (>20% features) | Incident L3 | Incident L3 + regulatory assess | — |
| Fairness DI < 0.80 | Incident L3 | Incident L3 + immediate Compliance | Domain-specific DI floor |

---

*End of EVA Rule Engine Specification v1.0*
