# DomainAnalysisRules (Lite)
## Quick Domain Analysis for EVA DPSU Agent
**Version:** 3.0-lite (Aligned with Enterprise 3.0)

---

## Task

Analyze the raw dataset profile and produce a `DatasetIdentity` object.

## Output Schema

Return a JSON object matching `gal_schema.py`:

```json
{
  "domain": "BANKING",
  "dataset_type": "TABULAR",
  "has_target_column": true,
  "inferred_target_column": "loan_default",
  "label_type": "BINARY",
  "has_temporal_column": false,
  "temporal_column_name": null,
  "has_group_column": false,
  "group_column_name": null,
  "has_pii_detected": false,
  "pii_column_candidates": [],
  "protected_attribute_flag": false,
  "n_rows": 10000,
  "n_features": 45,
  "domain_risk_flag": "HIGH",
  "regulatory_exposure_flag": true
}
```

## Key Rules

### Dataset Type Classification
- **PANEL**: Has both temporal and group columns.
- **TIME_SERIES**: Has temporal column only.
- **TABULAR**: Standard numeric/categorical columns.
- **NLP**: Long text columns (avg length > 50 chars).
- **UNKNOWN**: All other cases.
- **HARD_STOP**: If `dataset_type == UNKNOWN`.

### Domain Detection
- **BANKING**: Columns like `loan`, `credit`, `interest_rate`, `account`, `default`, `balance`.
- **HEALTHCARE**: Columns like `patient`, `diagnosis`, `treatment`, `blood`, `clinical`, `mortality`.
- **INSURANCE**: Columns like `policy`, `premium`, `claim`, `coverage`, `insured`.
- **GENERAL**: None of the above match.
- **OVERRIDE**: Always respect user-stated domain if provided.

### Target Classification
- Detect `label_type`:
  - Binary (0/1, yes/no) → `BINARY`
  - Few categories (2-20) → `MULTICLASS`
  - Continuous float → `REGRESSION`
- `high_risk_target_detected`: If target is `default`, `mortality`, `fraud`, `claim_loss`, or `diagnosis`.

### Simplified Risk Assessment
- **CRITICAL**: If `high_risk_target_detected == true`.
- **HIGH**: Elif domain is `BANKING`, `HEALTHCARE`, or `INSURANCE`.
- **LOW**: Otherwise.
- `regulatory_exposure_flag`: Set to `true` if domain is NOT `GENERAL`.

## Deterministic Constraints
- No escalation triggers.
- No SLA or regulatory matrices.
- Single-pass logic only.

