# IntentInferenceRules (Lite)
## Quick Intent Inference for EVA QBII Agent
**Version:** 3.0-lite

---

## Task
Infer a structured `UserIntentRecord` from user answers and `DatasetIdentity`.

## Output Schema
Return a JSON object matching `gal_schema.py`:

```json
{
  "primary_objective": "PREDICT",
  "deployment_mode": "HUMAN_REVIEWED",
  "decision_impact": "FINANCIAL_INDIVIDUAL",
  "risk_tier": "TIER_1",
  "interpretability_tier": 1,
  "regulatory_mode": "REGULATED",
  "regulatory_frameworks": ["INTERNAL"],
  "error_cost_direction": "FN_DOMINANT",
  "cost_matrix": {
    "cost_asymmetry": "HIGH"
  },
  "time_awareness": "NONE",
  "temporal_split_required": false,
  "inference_confidence": "HIGH",
  "escalation_required": false,
  "escalation_reasons": []
}
```

## Simplified Inference Rules

### 1. Risk Tier
- **TIER_1**: If `decision_impact` affects individuals (Financial, Health, Legal).
- **TIER_2**: Elif `deployment_mode` is `AUTOMATED`.
- **TIER_3**: Otherwise (Operational/Analytical with human review).

### 2. Interpretability Tier
- **1**: If `risk_tier == TIER_1`.
- **2**: If `risk_tier == TIER_2`.
- **3**: If `risk_tier == TIER_3`.

### 3. Regulatory Mode
- **REGULATED**: If `domain` is `BANKING`, `HEALTHCARE`, or `INSURANCE`.
- **STANDARD**: Otherwise.
- *Ignore GDPR_STRICT logic in Lite.*

### 4. Cost Direction
- Store `error_cost_direction` and `cost_asymmetry` directly from user answers.

## Constraints
- **Single-pass logic only**.
- No risk elevation matrix or regulatory precedence.
- No confidence scoring matrix.
- **HARD_STOP**: Only if `primary_objective == PREDICT` and no target column exists.

