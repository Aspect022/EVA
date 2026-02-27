# QuestionBuilderRules (Lite)
## Quick Question Generation for EVA QBII Agent
**Version:** 3.0-lite

---

## Task
Generate **3-5 plain-language questions** to determine user intent.

## Rules
- **Max 5 questions**.
- No algorithm jargon.
- No Regulatory, Fairness, or Interpretability questions.
- No Ambiguity gate or Escalation registry.

## Question Definitions

| Type | Field | Description |
|------|-------|-------------|
| `goal` | `primary_objective` | Predict, explain, segment, detect anomalies, or forecast? |
| `deployment` | `deployment_mode` | Automated, human-reviewed, or hybrid? |
| `impact` | `decision_impact` | Who/what does this decision affect (individuals, operations, or analytics)? |
| `error_cost` | `error_cost_direction` | Which error is worse: missing a case or a false alarm? |
| `time` | `time_awareness` | Does the sequence of events over time matter? |

## Conditional Logic
1. **Always ask** `goal`.
2. **If goal is predictive**: ask `deployment` and `impact`.
3. **If predictive + automated/hybrid**: ask `error_cost`.
4. **If temporal data detected**: ask `time`.

## Output Contract
Return a `RawAnswerRecord` (JSON) matching `gal_schema.py`:

```json
{
  "questions": [
    {
      "question": "text",
      "question_type": "goal | deployment | impact | error_cost | time",
      "why_asked": "reason"
    }
  ],
  "ambiguity_flags": [],
  "conservative_fallbacks_applied": []
}
```

## Hard Stop
- **PREDICT** + no target column detected in `DatasetIdentity`.

