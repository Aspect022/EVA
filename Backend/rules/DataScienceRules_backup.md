# EVA Data Science Rules
## Strategy Agent Reference Guide

> **Note:** This is a starter set of rules. You will expand this into a detailed
> checklist with domain-specific guidance. For now, these are the foundational
> principles that every Strategy Agent MUST follow when reasoning about data.

---

### 1. UNDERSTAND BEFORE YOU ACT
Never propose a cleaning action without first understanding what the column
represents in the real world. A "null" in a medical column means something
very different from a "null" in a click-stream column.

### 2. PRESERVE ORIGINAL DATA
The original dataset is sacred. All modifications happen on a COPY. The
snapshot must remain untouched for auditability.

### 3. IMPUTATION > DROPPING
Prefer imputation over dropping rows/columns. Only drop when:
- Column has >60% missing values AND is not critical to the analysis goal.
- Rows are exact duplicates.

### 4. USE STATISTICALLY SOUND IMPUTATION
- **Numerical columns**: Use median (robust to outliers) or KNN imputation
  if column relationships are strong. Never use mean for skewed distributions.
- **Categorical columns**: Use mode. If cardinality is high, consider
  grouping rare categories into "Other" before imputing.
- **Time-series data**: Use forward-fill or interpolation, never random fill.

### 5. RESPECT THE TARGET VARIABLE
- Never impute or transform the target variable without explicit user consent.
- Never drop rows that have valid target values unless corruption is proven.
- Flag any target leakage risks in the strategy.

### 6. TYPE CORRECTION IS NON-NEGOTIABLE
- If a column looks numeric but is stored as string (e.g., "$100" or "1,200"),
  clean and convert it.
- Date columns stored as strings must be parsed into proper datetime types.
- Boolean columns stored as "Yes"/"No" must be converted to True/False.

### 7. DOCUMENT EVERY CHANGE
Every modification must have a clear record of:
- **What** was changed (column, rows affected)
- **Why** it was changed (the real-world reasoning)
- **How** it was changed (the technique used)
- **What alternatives** were considered and rejected

### 8. OUTLIER HANDLING IS CONTEXT-DEPENDENT
- Do NOT automatically remove outliers. A $10M transaction might be fraud
  in retail but normal in enterprise B2B.
- Flag outliers (>3 IQRs) but only remove if domain context supports it.
- Always prefer capping/winsorizing over deletion.

### 9. ENCODING COMES AFTER CLEANING
- Do not encode categorical variables during the cleaning phase.
- Encoding is a feature engineering decision, not a data repair decision.
- Cleaning phase only ensures values are consistent (e.g., "Male" vs "male" vs "M").

### 10. DUPLICATES REQUIRE JUDGMENT
- Exact row duplicates: safe to remove.
- Near-duplicates: flag but don't remove without context.
- Time-stamped duplicates may be legitimate repeated events.

### 11. COLUMN CONSISTENCY
- Standardize string casing (lowercase or titlecase, pick one).
- Strip leading/trailing whitespace from all string values.
- Normalize unicode characters if present.

### 12. MISSING VALUE PATTERNS MATTER
- Check if missingness is random (MCAR), systematic (MAR), or structural (MNAR).
- MNAR data (e.g., income missing because people don't report it) requires
  domain-specific handling, not simple imputation.
- Document the missingness pattern in the strategy output.

### 13. CORRELATION-AWARE DECISIONS
- When two columns are highly correlated (|r| > 0.9), consider whether
  both are needed. Flag potential multicollinearity.
- Use correlation to guide imputation — if column A predicts column B well,
  use A to impute B.

### 14. FAIL SAFE
- If the Strategy Agent is uncertain about a cleaning decision, it should
  default to the most conservative option (preserve data, flag for review).
- High-confidence decisions: proceed. Low-confidence: document uncertainty.

### 15. USER INTENT DRIVES PRIORITY
- If the user's goal is PREDICTION, prioritize target integrity and feature completeness.
- If the goal is EXPLANATION, prioritize interpretability and avoid aggressive transforms.
- If the goal is SEGMENTATION, prioritize categorical consistency and completeness.
