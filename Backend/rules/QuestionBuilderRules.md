# Question Builder Rules

These rules dictate how EVA's Question Builder & Intent Inference (QBII) module generates questions for the user.

## Core Objective

Generate 3 to 5 SHORT, decision-focused, plain-language questions to understand what the user wants to accomplish with the dataset, given its domain identity.

## Rules

1. **Plain Language:** Never ask the user to pick an algorithm, metric, or technical parameter (e.g., do not ask "Do you want to use Random Forest?").
2. **Context-Driven:** Derive questions from the provided dataset `DatasetIdentity` (domain, time behavior, column roles).
3. **Mandatory Question Types:**
    * **Goal:** At least one question about the overall objective ("What are you trying to figure out?").
    * **Stakeholder:** At least one question about who consumes the result ("Who will see the results?").
    * **Priority:** At least one question about tradeoffs ("Accuracy vs explainability?").
    * **Time (Conditional):** Only ask about time/forecasting if the dataset has time-series or event-log behavior.
4. **Structured Output:** Each question must have a `question_type` (goal, stakeholder, priority, time) and a `why_asked` explanation.
