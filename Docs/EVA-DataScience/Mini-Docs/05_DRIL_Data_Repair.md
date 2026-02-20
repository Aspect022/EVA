# DRIL — Data Repair & Integrity Layer
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Data Repair & Integrity Layer is responsible for preparing the dataset for reliable analysis. Its goal is not to produce a "perfect" dataset. Its goal is to produce a trustworthy one — a dataset whose contents can be relied upon to reflect reality rather than artifacts of how the data was collected, stored, or transmitted.

DRIL corrects what needs correcting, leaves alone what should be left alone, and records everything with explicit reasoning. It is the module that ensures every conclusion EVA later draws is built on a foundation that can be defended.

---

## 2. Design Principle

Data imperfection is not a technical problem to be solved mechanically. It is a reflection of the real-world processes that produced the data.

Missing values appear because measurements were not taken, not recorded, or not applicable. Outliers exist because rare events happen. Duplicates appear because systems record things more than once. Imbalance exists because certain outcomes are genuinely uncommon.

These are not all errors. Some are meaningful signals about reality. Removing them without thought destroys information. Keeping them without thought distorts analysis. The right choice depends on what the data represents and what the analysis is trying to accomplish.

DRIL follows three rules that emerge from this principle:

**Not all irregularities should be removed.** Some contain important information.

**Cleaning decisions must depend on context.** The same missing value may be filled, flagged, or kept depending on what the column represents and what the analysis needs.

**Every modification must be justified.** A change that cannot be explained should not be made.

---

## 3. Position in the Pipeline

**Comes after:** QBII (Stage 1). DRIL needs both the dataset identity from DPSU and the user's intent from QBII before making any decisions.

**Comes before:** EPR (Stage 3). Exploration must be performed on clean, reliable data. Patterns discovered in dirty data cannot be trusted.

**Rule:** DRIL must read both Section 1 (Dataset Identity) and Section 2 (User Intent) of the GAL before taking any action.

---

## 4. Inputs

**From the GAL:**
- Section 1 — Dataset Identity (row meaning, column roles, time behavior, misinterpretation risks, data health warnings)
- Section 2 — User Intent (selected target, analysis type, success definition)

**From the dataset:**
- The raw dataset as uploaded

DRIL operates on the dataset with full knowledge of what it represents and what it is being used for. This context determines every decision it makes.

---

## 5. Core Responsibilities

1. Detect and evaluate missing values
2. Detect and resolve duplicates
3. Detect and correct data type problems
4. Evaluate and handle outliers and noise
5. Assess class imbalance (when a target exists)
6. Detect and flag data leakage risks
7. Validate the repaired dataset before releasing it to the next stage
8. Record every action and its justification in the GAL

---

## 6. Process

### Step 1 — Read Context Before Acting

Before inspecting the data for problems, DRIL reads the full context from the GAL. The column role map tells it which columns are identifiers (and therefore should not be imputed or engineered). The time behavior tells it whether forward-fill strategies are appropriate. The user intent tells it which columns are critical to the analysis and therefore must be handled with extra care.

This step is not optional. An imputation strategy that is correct for a feature column may be completely wrong for a target column. DRIL cannot make sound decisions without knowing which is which.

### Step 2 — Missing Value Evaluation

For each column with missing values, DRIL asks three questions before choosing a strategy.

**How much is missing?** A column that is 2% missing is a different problem from a column that is 60% missing. High missingness may indicate the column is not reliably collected and should be treated with caution throughout the analysis.

**Where is it missing?** Is missingness random — spread across rows with no apparent pattern? Or is it concentrated — missing for a particular group, time period, or condition? Concentrated missingness is often meaningful. It may indicate that certain cases were handled differently, or that certain data sources did not capture a particular measurement.

**Does missingness itself carry meaning?** In some domains, the absence of a value is informative. A patient with no recorded medication may genuinely be unmedicated — which is a meaningful fact, not a gap. A customer with no purchase history may be a new customer or a churned one. In these cases, imputing a value destroys the signal.

**After answering these questions, DRIL selects a strategy:**

*Retain and flag* — if missingness is meaningful, create a binary indicator column marking which rows had missing values, then either leave the original column missing or apply a neutral fill. The indicator preserves the information.

*Statistical replacement* — if missingness is random and the column is a numeric feature, fill with an appropriate central value. What "appropriate" means depends on the distribution and the domain.

*Conditional replacement* — if missingness is non-random but the pattern is understood, fill using the values of related columns. For example, fill missing age with the median age for the same customer segment.

*Forward-fill or backward-fill* — for time series data, propagate the most recent known value forward (or the next known value backward). This assumes the value did not change between measurements, which is only appropriate for slowly-changing variables.

*Removal* — if a row or column is missing too much data to be useful, it may be removed. This is a last resort. Removing rows reduces the dataset. Removing columns loses information. Both actions require explicit justification.

**What DRIL records for each missing value decision:**
- Which column, how much was missing, where it was missing
- The strategy chosen and why
- What the chosen strategy assumes about the data
- What the alternative strategies were and why they were not chosen
- How many rows were affected

### Step 3 — Duplicate Detection and Resolution

DRIL identifies rows that appear more than once in the dataset.

**Exact duplicates** — rows that are identical across every column — are almost always errors. They suggest the same event was recorded twice, which would bias any aggregation or count. DRIL removes exact duplicates and records how many were removed.

**Near duplicates** — rows that are identical across most columns but differ slightly — require more careful handling. They may be errors, or they may represent genuinely distinct events that happen to look similar. DRIL evaluates near duplicates in light of the row meaning.

If the row represents a transaction and two rows share the same transaction ID with slightly different amounts, that is likely a data error. If the row represents a patient visit and two rows share the same patient with slightly different recorded weights, that may be legitimate measurement variation.

Near duplicates are flagged in the GAL with an explanation of why they were kept or removed. They are not silently deleted.

**The row meaning from DPSU is critical here.** What counts as a duplicate is a semantic question, not a mechanical one.

### Step 4 — Data Type Corrections

DRIL detects columns stored in an incorrect format and corrects them where the interpretation is unambiguous.

Common type problems:
- Numeric values stored as text (e.g., "42" instead of 42)
- Dates stored as strings (e.g., "January 15 2023" instead of a parseable date)
- Boolean values stored as various text encodings (e.g., "Yes"/"No", "1"/"0", "True"/"False")
- Categorical variables stored as numeric codes without a key

**Rule:** If the correct type is unambiguous, DRIL corrects it and records the correction. If the correct type is ambiguous — for example, a column of numbers that might be an identifier, a ranking, or a true quantity — DRIL flags the ambiguity in the GAL and does not automatically convert. The ambiguity is noted for later modules to consider.

### Step 5 — Outlier and Noise Evaluation

Extreme values require careful evaluation. Not all outliers are errors. Some represent the most important cases in the dataset.

**The question DRIL asks is not "is this value extreme?" but "is this value real?"**

DRIL evaluates each apparent outlier against:
- What the column represents (a customer who spent $50,000 may be an unusually high-value customer, not an error)
- What the domain context suggests (a blood pressure reading of 300 mmHg is medically implausible; one of 160 mmHg is unusual but possible)
- What the user's goal is (if the goal is detecting anomalies, outliers are the most valuable rows in the dataset; they must not be removed)

**Possible actions:**

*Keep unchanged* — if the value is plausible and the analysis either is not affected by or specifically benefits from it.

*Cap or clip* — if extreme values distort aggregations but should still be represented, replace them with a threshold value. This preserves the information that an extreme value occurred without letting it dominate everything else.

*Flag for analysis* — mark the row as containing an extreme value and let later stages (IHE, VPE) decide whether to investigate it.

*Remove* — only if the value is implausible, verified as an error, and would meaningfully distort the analysis. This is the last resort, and it requires explicit justification.

**What DRIL records:** The value or range, why it was considered an outlier, the action taken, the reasoning, and what would have been the alternative.

### Step 6 — Class Imbalance Assessment

If a target variable was identified and confirmed by QBII, DRIL evaluates whether the distribution of outcome classes is severely imbalanced.

**What constitutes severe imbalance** depends on context. A dataset where 5% of cases are fraudulent is imbalanced but not unusually so for fraud data. A dataset where 0.1% are fraudulent may cause analysis techniques to systematically ignore the minority class.

DRIL does not apply resampling or weighting directly. Its role is to assess and record:
- The class distribution
- Whether the imbalance is likely to distort the analysis
- What approaches might address it (to be considered by later stages)

The assessment is recorded in the GAL. It becomes a constraint that later modules must acknowledge.

### Step 7 — Leakage Detection

Data leakage is one of the most damaging and hardest-to-detect problems in data analysis. It occurs when a column contains information that would not be available at the time a real-world decision would be made — information that effectively tells the analysis the answer before the question has been asked.

Leakage makes results look better than they are and makes models that fail catastrophically in real use.

**DRIL detects leakage through a structured reasoning process:**

*Step 7a — Timeline reasoning.* For each column, DRIL reasons about when that information would be known relative to when the outcome occurs. If the dataset tracks customer churn, any column that is only recorded after a customer has churned is leakage. Examples: "cancellation_date," "reason_for_leaving," "days_before_cancellation_was_filed."

*Step 7b — Outcome encoding detection.* DRIL looks for columns that represent the same information as the target variable in a different form. If the target is "churned" (yes/no), then a column called "contract_status" with values "active" and "terminated" is likely encoding the same thing. Including it in the analysis would be circular.

*Step 7c — Aggregate features containing the target.* If any columns appear to be computed statistics that include the outcome — for example, a "total_lifetime_value" column computed after factoring in whether the customer churned — these are leakage.

*Step 7d — ID columns with embedded temporal information.* Sequential identifiers that were assigned over time can accidentally encode temporal information. If earlier-assigned customers behave differently from later ones, and the ID encodes which is which, using the ID as a feature causes the analysis to learn time effects through a proxy.

**What happens with detected leakage:**

Columns identified as leakage are flagged as restricted in the GAL. The restriction is recorded with a plain-language explanation of what the leakage is and why it is problematic. Later modules cannot use restricted columns as features or include them in analysis without explicitly acknowledging and overriding the restriction with justification.

**Rule:** Leakage detection is not optional. It must be performed when a target variable exists.

### Step 8 — Validation

After all repairs are complete, DRIL performs a final validation pass before releasing the dataset.

**The validation confirms:**
- The dataset still represents the same real-world process it did before cleaning (no accidental semantic distortion)
- The target variable remains meaningful and has not been corrupted
- No new inconsistencies were introduced by the repair operations
- Column roles assigned by DPSU are still valid after cleaning
- The repaired dataset is consistent with the Data Integrity Record written during this stage

If validation fails, the specific failure is recorded in the GAL and the affected cleaning decisions are reconsidered. The pipeline does not advance until validation passes.

---

## 7. Output Written to the GAL

DRIL writes Section 3 — Data Integrity Record. For every action taken:

- **Problem Identified** — what issue existed and in which column(s)
- **Impact Assessment** — why this problem matters for this specific analysis
- **Action Taken** — the correction strategy applied
- **Alternatives Considered** — other strategies that were evaluated and why they were not chosen
- **Effect on Dataset** — how many rows or values were affected
- **Confidence Level** — how certain DRIL is that the chosen strategy was correct
- **Residual Risk** — any remaining concern or uncertainty introduced by the choice

**Additionally:**
- A list of restricted columns (flagged for leakage or misinterpretation risk) with explanations
- The final validation result

---

## 8. Failure Handling

**Column critical to analysis has too much missing data to be reliably imputed:** DRIL records this as a significant limitation. It does not silently drop the column or silently impute it. It records the problem, the options, and what was chosen — and flags the analysis as having a known limitation that must be communicated in the final report.

**Leakage detected but user's goal requires using the column:** This is a conflict that cannot be silently resolved. DRIL records the leakage, applies the restriction, and notes the conflict. If the user's goal genuinely requires the column, QBII may need to be revisited to clarify the intent.

**Duplicate detection produces ambiguous results:** If DRIL cannot determine whether near-duplicate rows are errors or genuine, it retains them, flags them clearly in the GAL, and notes that downstream analyses may be affected.

**Validation fails after cleaning:** DRIL identifies which cleaning operation caused the failure, records the failure, and revisits the decision. If the failure cannot be resolved, the GAL records the unresolved problem and its potential impact on the analysis.

---

## 9. Operational Rules

1. DRIL must read Sections 1 and 2 of the GAL before taking any action.
2. No modification to the dataset may occur without a corresponding GAL entry with justification.
3. The original state of the dataset must remain reconstructable from the Data Integrity Record.
4. Removal of rows or columns requires explicit justification — it is never the default.
5. Leakage detection must be performed when a target variable exists. It is not optional.
6. Validation must pass before the dataset is released to EPR.
7. Every restriction applied to a column must be recorded with a plain-language explanation of why.

---

## 10. Dependency Map

**Reads from:**
- GAL Section 1 — Dataset Identity (column roles, time behavior, health warnings, misinterpretation risks)
- GAL Section 2 — User Intent (selected target, analysis type)
- Raw dataset

**Writes to:** GAL Section 3 — Data Integrity Record

**Feeds into:**
- EPR (exploration is performed on the repaired dataset)
- IHE (hypotheses must account for data limitations recorded here)
- FIE (feature engineering must respect restricted columns)
- RG (the report explains what was repaired and why, to reassure the reader)
