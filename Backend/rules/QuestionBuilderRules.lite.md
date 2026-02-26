# QuestionBuilderRules (Lite)
## Quick Question Generation for EVA QBII Agent
**Version:** 1.0-lite (see QuestionBuilderRules.md for full version)

---

## Rules

- Generate **3-5 plain-language questions** based on the dataset profile.
- No algorithm or technical jargon. Write for a business user.
- Each question must have: `question`, `question_type`, `why_asked`.

## Question Types

| Type | Purpose |
|------|---------|
| `goal` | What does the user want to achieve? (predict, explain, segment, detect anomalies, forecast) |
| `stakeholder` | Who will use the results and how? |
| `priority` | What matters more — accuracy or explainability? Any regulatory needs? |
| `time` | Does time ordering matter in this dataset? |

## Mandatory First Question

Always ask the user what their primary goal is:
- Predict an outcome
- Explain what drives an outcome
- Group/segment records
- Detect anomalies
- Forecast future values

## Conditional Questions

- If the dataset has a temporal column → ask about time sensitivity.
- If domain is BANKING/HEALTHCARE/INSURANCE → ask about regulatory/compliance needs.
- If a target column exists → ask about error cost preference (missing a case vs false alarm).

## Output Format

Return a JSON object:
```json
{
  "questions": [
    {
      "question": "What is the primary goal of this analysis?",
      "question_type": "goal",
      "why_asked": "Determines the modeling strategy"
    }
  ]
}
```
