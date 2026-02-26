# DomainAnalysisRules (Lite)
## Quick Domain Analysis for EVA DPSU Agent
**Version:** 1.0-lite (see DomainAnalysisRules.md for full version)

---

## Task

Analyze the raw dataset profile and produce a `DatasetIdentity` object.

## Output Schema

Return a JSON object with these fields:

```json
{
  "domain": "BANKING | HEALTHCARE | INSURANCE | GENERAL | UNKNOWN",
  "dataset_type": "TABULAR | TIME_SERIES | PANEL | NLP | CV | GRAPH | UNKNOWN",
  "has_target_column": true,
  "inferred_target_column": "column_name or null",
  "label_type": "BINARY | MULTICLASS | REGRESSION | NONE | UNKNOWN",
  "has_temporal_column": true,
  "temporal_column_name": "column_name or null",
  "has_group_column": false,
  "group_column_name": null,
  "has_pii_detected": false,
  "pii_column_candidates": [],
  "protected_attribute_flag": false,
  "n_rows": 1000,
  "n_features": 15,
  "domain_risk_flag": "LOW | MODERATE | HIGH | CRITICAL",
  "regulatory_exposure_flag": false
}
```

## Key Rules

### Domain Detection
- **BANKING**: columns like `loan`, `credit`, `interest_rate`, `account`, `default`, `balance`.
- **HEALTHCARE**: columns like `patient`, `diagnosis`, `treatment`, `blood`, `clinical`, `mortality`.
- **INSURANCE**: columns like `policy`, `premium`, `claim`, `coverage`, `insured`.
- **GENERAL/UNKNOWN**: none of the above patterns match.

### Dataset Type
- Has temporal + group column → `PANEL`
- Has temporal column only → `TIME_SERIES`
- Standard numeric/categorical → `TABULAR`
- Long text columns (avg length > 50 chars) → `NLP`

### Target Column
- Look for columns named: `target`, `label`, `outcome`, `flag`, `default`, `churn`, `fraud`, `survived`.
- Binary (0/1, yes/no) → `BINARY`
- Few categories (2-20) → `MULTICLASS`
- Continuous float → `REGRESSION`
- No match → `NONE`

### Risk Assessment
- BANKING/HEALTHCARE/INSURANCE → `HIGH` or `CRITICAL` risk, `regulatory_exposure_flag = true`
- GENERAL → `LOW` risk

### PII Detection
- Flag columns with names like: `name`, `email`, `phone`, `ssn`, `address`, `dob`, `birth`.
