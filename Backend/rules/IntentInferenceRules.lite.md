# IntentInferenceRules (Lite)
## Quick Intent Inference for EVA QBII Agent
**Version:** 1.0-lite (see IntentInferenceRules.md for full version)

---

## Task

Given the user's answers to QBII questions and the DatasetIdentity, infer a structured `UserIntentRecord`.

## Output Schema

Return a JSON object with these fields:

```json
{
  "primary_objective": "PREDICT | EXPLAIN | SEGMENT | ANOMALY_DETECT | FORECAST",
  "deployment_mode": "AUTOMATED | HUMAN_REVIEWED | HYBRID",
  "decision_impact": "FINANCIAL_INDIVIDUAL | HEALTH_SAFETY | LEGAL_STATUS | OPERATIONAL | ANALYTICAL",
  "risk_tier": "TIER_1 | TIER_2 | TIER_3",
  "interpretability_tier": 1 | 2 | 3,
  "regulatory_mode": "STANDARD | REGULATED | GDPR_STRICT",
  "regulatory_frameworks": ["NONE"],
  "error_cost_direction": "FN_DOMINANT | FP_DOMINANT | SYMMETRIC | UNKNOWN",
  "fairness_sensitivity": "LOW | MODERATE | HIGH",
  "time_awareness": "FORECAST | POINT_IN_TIME_STRICT | TREND_ANALYSIS | NONE",
  "temporal_split_required": false,
  "explanation_requirement": "INDIVIDUAL_FACING | AUDIT_FACING | BOTH | NONE",
  "inference_confidence": "HIGH | MEDIUM | LOW",
  "escalation_required": false,
  "escalation_reasons": [],
  "conservative_overrides_applied": []
}
```

## Key Inference Rules

1. **primary_objective**: Map directly from the user's goal answer.
2. **risk_tier**: TIER_1 if decisions affect individuals (finance, health, legal). TIER_2 for operational. TIER_3 for analytics/research.
3. **interpretability_tier**: 1 if TIER_1 risk or individual-facing explanations needed. 2 for audit-facing. 3 for internal only.
4. **regulatory_mode**: REGULATED if domain is BANKING/HEALTHCARE/INSURANCE. GDPR_STRICT if privacy law applies. STANDARD otherwise.
5. **deployment_mode**: AUTOMATED if fully automatic. HUMAN_REVIEWED if a person reviews. HYBRID if flagging for review.
6. **error_cost_direction**: FN_DOMINANT if missing real cases is worse. FP_DOMINANT if false alarms are worse. SYMMETRIC if equal.
7. **time_awareness**: Set based on whether temporal patterns matter for the analysis.

## Conservative Defaults

When uncertain, use conservative values:
- `risk_tier` → `TIER_1`
- `interpretability_tier` → `1`
- `regulatory_mode` → `REGULATED`
- `deployment_mode` → `HUMAN_REVIEWED`
- Mark overridden fields in `conservative_overrides_applied`.
