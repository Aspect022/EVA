# Intent Inference Rules

These rules dictate how EVA's Question Builder & Intent Inference (QBII) module infers the structured user intent from their answers.

## Core Objective

Infer a structured analytical intent (`UserIntentRecord`) from the user's free-text responses, combined with the dataset context.

## Rules

1. **Analysis Type:** Determine if the goal is `prediction`, `explanation`, `segmentation`, `anomaly_detection`, `monitoring`, or `reporting`.
2. **Stakeholder Type:** Identify the consumer as `student`, `business_owner`, `researcher`, `analyst`, or `manager`.
3. **Interpretability Priority:** Determine if the need for explainability is `high`, `moderate`, or `low`.
4. **Inference & Defaults:**
    * If answers are vague, infer the most likely values using the dataset context.
    * Record which fields were inferred (not explicitly stated) in the `inferred_elements` list.
    * Conservative defaults: If unsure between explanation and prediction, choose `explanation`. If unsure about stakeholder, choose `analyst`. If unsure about interpretability, choose `high`.
5. **Target Variable:** If the user's goal involves prediction, confirm or select a target variable from the `target_candidates` provided in the dataset identity.
