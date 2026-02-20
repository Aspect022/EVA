# EPR — Exploration & Pattern Recognition
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Exploration & Pattern Recognition module discovers what is actually happening in the cleaned dataset. It is the evidence-gathering stage — the systematic search for patterns, relationships, anomalies, and trends that exist in the data before any attempt to explain them.

EPR produces observations only. Not explanations, not recommendations, not hypotheses. Those come in the next stage. EPR's discipline is to describe what exists, precisely and without interpretation, so that the IHE has a clean, evidence-based foundation to reason from.

This separation between observation and explanation is not pedantic. It is one of EVA's most important design decisions. When observation and explanation are mixed, the explanation shapes what is observed — analysts unconsciously find patterns that support the story they have already started telling. By separating them into distinct stages with a documented record between them, EVA ensures that hypotheses are formed in response to findings, not the other way around.

---

## 2. Design Principle

Most automated systems generate a standard set of exploratory outputs: distributions, correlation matrices, missing value heatmaps. They produce these because the data exists, not because a specific question demands them.

EVA's exploration is guided by context. The domain, the row meaning, the user's analytical goal, and the data's time behavior all shape which patterns are worth looking for and how to interpret what is found. A correlation that is meaningful in a customer behavior context may be irrelevant in a sensor monitoring context. A distribution that is alarming in a healthcare dataset may be completely normal in a finance dataset.

The discipline of EPR: **find patterns that are real, report them precisely, and leave interpretation to the next stage.**

---

## 3. Position in the Pipeline

**Comes after:** DRIL (Stage 2). Exploration must be performed on the clean, repaired dataset. Patterns found in dirty data cannot be trusted — they may reflect data quality problems, not real-world behavior.

**Comes before:** IHE (Stage 4). The IHE needs EPR's findings to know what to explain.

**Rule:** EPR must read Sections 1, 2, and 3 of the GAL before beginning. Dataset identity shapes what to look for. User intent determines which patterns are most important. The data integrity record tells EPR what limitations exist in the cleaned data.

---

## 4. Inputs

**From the GAL:**
- Section 1 — Dataset Identity (row meaning, domain, time behavior, column roles — shapes what patterns are meaningful)
- Section 2 — User Intent (analytical goal and target — determines which patterns are highest priority)
- Section 3 — Data Integrity Record (data limitations — affects confidence in findings)

**From the dataset:**
- The cleaned, validated dataset produced by DRIL

---

## 5. Core Responsibilities

1. Explore distributions of key variables
2. Identify correlations and assess their strength
3. Detect natural groupings or segments
4. Surface anomalies and unusual observations
5. Analyze temporal patterns for time-dependent datasets
6. Identify variables most associated with the target (when one exists)
7. Prioritize findings by relevance to the user's analytical goal
8. Record all findings precisely in Section 4 of the GAL

---

## 6. Process

### Step 1 — Establish Exploration Priorities

Before exploring anything, EPR reads the user intent from Section 2 of the GAL and establishes what kinds of patterns matter most for this specific analysis.

If the goal is understanding what drives customer churn, patterns involving the target variable (churned/not churned) are the highest priority. Group differences, correlations with the target, and behavioral sequences before churning are what to look for most carefully.

If the goal is segmentation, natural groupings within the data are the highest priority. Variables that differentiate potential clusters are most important.

If the goal is anomaly detection, unusual observations are the highest priority. The baseline "normal" behavior must be established so that deviations from it can be identified.

This prioritization does not mean ignoring other patterns. It means knowing which patterns to report most prominently and which to treat as secondary.

### Step 2 — Distribution Analysis

For each key variable, EPR examines how values are distributed across the dataset.

What EPR records:
- The overall shape of the distribution (concentrated, spread, skewed, bimodal)
- Where the bulk of values sit
- Whether there are unusual concentrations or gaps
- The presence of extreme values at either end
- Whether the distribution is consistent with what the domain would suggest is normal

Distribution findings are recorded as observations. Not "this is too skewed" but "this variable has a heavily right-skewed distribution, with most values below X and a long tail extending to Y." The observation is the fact. Whether it is a problem, or what it means, is determined by IHE.

### Step 3 — Correlation and Relationship Analysis

EPR examines how variables relate to each other and, where a target exists, how each variable relates to the target.

What EPR records:
- Which variable pairs show meaningful relationships
- The direction and approximate strength of each relationship
- Whether relationships appear linear or follow a different pattern
- Whether relationships are consistent across the dataset or vary by segment
- Variables that show strong associations with the target

Relationships are recorded as observed associations, not as causes. "Variable A is strongly associated with Variable B" is an observation. "Variable A causes Variable B" is a hypothesis — it goes in Section 5, not Section 4.

### Step 4 — Segment Detection

EPR looks for natural groupings within the data — subsets of the population that behave meaningfully differently from each other.

What EPR records:
- Whether distinct groups exist and on what basis they differ
- How the groups differ in their key characteristics
- How large each group is relative to the total
- Whether the groups differ in their relationship to the target (if one exists)

Segments are reported as observations: "there appear to be three distinct behavioral groups, characterized by their differences in frequency, recency, and monetary value." Whether these groups represent customer lifecycle stages, risk categories, or something else entirely is a matter for IHE.

### Step 5 — Anomaly Detection

EPR identifies observations that are unusual relative to the rest of the dataset.

An anomaly is not simply an outlier. An outlier is a value at the extreme of a distribution. An anomaly is a combination of values — or a single extreme value — that is unusual in a way that may be meaningful. The distinction matters because not all outliers are anomalies and not all anomalies are obvious outliers.

What EPR records:
- Which specific records or groups of records are anomalous
- What makes them anomalous (which variables, what values)
- How unusual they are relative to the rest of the dataset
- Whether the anomaly is concentrated in a specific time period, segment, or condition

EPR does not determine whether anomalies are errors or meaningful events. That requires context and judgment — the work of IHE.

### Step 6 — Temporal Analysis (for time-dependent datasets)

For datasets classified as time series, event logs, or panel data in Section 1 of the GAL, EPR performs a dedicated temporal analysis.

What EPR examines:
- Whether there is an overall trend (increasing, decreasing, stable, cyclical)
- Whether there are seasonal or cyclical patterns
- Whether there are sudden changes at specific points in time (step changes)
- Whether the rate of change has accelerated or decelerated
- Whether temporal patterns are consistent across entities (for panel data) or concentrated in specific subsets

What EPR records: temporal patterns as observed facts. "Sales show a consistent decline in Q3 across all three years in the dataset" is an observation. "This is because of seasonal purchasing behavior" is a hypothesis.

### Step 7 — Prioritize and Summarize

After completing the exploration, EPR reviews all findings and assigns each one a relevance level relative to the user's analytical goal. The most relevant findings — those most directly related to what the user is trying to accomplish — are flagged as priority findings. These are the ones that IHE will focus on most intensively.

The full set of findings is recorded in the GAL. The priority designations help downstream modules allocate their attention appropriately.

---

## 7. Output Written to the GAL

EPR writes Section 4 — Exploratory Findings. Each entry contains:

- **Finding Description** — a precise, plain-language statement of what was observed
- **Variables Involved** — which columns or derived variables the finding involves
- **Strength of the Pattern** — how clear and consistent the pattern is
- **Relevance to User Goal** — how directly this finding relates to what the user is trying to accomplish (high, moderate, low)
- **Data Confidence** — any limitations from the Data Integrity Record that affect confidence in this finding
- **Finding Type** — distribution, correlation, segment, anomaly, or temporal

---

## 8. Failure Handling

**Dataset is too small to reveal meaningful patterns:** EPR records this as a fundamental limitation. The findings that can be observed are reported, but EPR notes prominently that the dataset size limits confidence in any pattern. IHE will generate lower-confidence hypotheses as a result.

**Exploration reveals only noise — no clear patterns:** This is itself a finding. EPR records that no meaningful patterns were identified and notes what this might imply (the variables in the dataset may not be the right ones for the analytical goal, or the dataset may be too small or too noisy to reveal structure).

**Data integrity limitations undermine specific findings:** If the Data Integrity Record notes significant missing data or imputation in a variable, EPR records this when reporting findings about that variable. Confidence in findings from heavily imputed columns is lower.

---

## 9. Operational Rules

1. EPR must operate on the cleaned dataset from DRIL, not the raw dataset.
2. EPR records observations only — no explanations, no hypotheses.
3. Findings must be stated precisely — with the variables, the direction, and the approximate magnitude of the pattern.
4. No finding may be omitted because it conflicts with another finding. Contradictory evidence is recorded as-is.
5. The relevance prioritization must reference the user intent from Section 2.
6. Data confidence limitations from Section 3 must be noted where they apply.

---

## 10. Dependency Map

**Reads from:**
- GAL Section 1 — Dataset Identity (row meaning, domain, column roles, time behavior)
- GAL Section 2 — User Intent (analytical goal, target variable)
- GAL Section 3 — Data Integrity Record (data limitations)
- Cleaned dataset (from DRIL)

**Writes to:** GAL Section 4 — Exploratory Findings

**Feeds into:**
- IHE (the findings are what IHE explains)
- FIE (findings may suggest useful feature transformations)
- VPE (findings are a primary source of visualization questions)
- ADC (key findings appear in Panel A and Panel B of the dashboard)
- RG (Section D of the report presents findings)
