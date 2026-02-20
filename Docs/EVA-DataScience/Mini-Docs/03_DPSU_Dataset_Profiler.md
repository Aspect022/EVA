# DPSU — Dataset Profiler & Semantic Understanding
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Dataset Profiler & Semantic Understanding module is responsible for building EVA's first mental model of an uploaded dataset. It is the foundation of the entire analysis. If this stage is wrong, every stage that follows is wrong.

Before any cleaning, any questioning, any exploration, or any feature engineering can begin, EVA must determine what the dataset represents in the real world. Not what its columns are called. Not what data types they carry. What they actually mean — what human activity or real-world process produced these rows.

This module answers the foundational question: **What does each row actually represent?**

---

## 2. Design Principle

Most automated data systems treat datasets as tables — collections of columns and rows to be processed. EVA treats datasets as records of real-world events.

A dataset is not just columns and rows. It is evidence of a process: a series of purchases, a set of patient visits, a stream of sensor readings, a history of employee records. The data exists because something happened in the world, and each row is a record of one instance of that something.

This distinction matters enormously. Two datasets with identical structure — same column types, same number of rows, same missing value rate — require completely different handling if one represents individual customer transactions and the other represents monthly account summaries. The cleaning strategies differ. The features that make sense differ. The visualizations that are meaningful differ. The hypotheses that are worth generating differ.

DPSU ensures that EVA knows which it is dealing with before touching anything.

---

## 3. Position in the Pipeline

**Comes before:** Everything. DPSU is Stage 0.

**Comes after:** Nothing. DPSU reads the raw dataset directly. It is the only module permitted to do so.

**Rule:** No other module may begin until DPSU has completed and written Section 1 of the GAL.

---

## 4. Inputs

DPSU reads the raw dataset directly. It does not receive any prior GAL context because none exists yet.

From the dataset, it reads:
- Column names and their structure
- Data types as stored
- Sample records (representative rows)
- Value distributions across columns
- Missing value patterns (which columns, how much, where)
- Unique value counts per column
- Basic statistical ranges

DPSU does not require user input to begin its work. It operates entirely from the data itself.

---

## 5. Core Responsibilities

DPSU must accomplish the following before writing to the GAL:

1. Determine what one row in the dataset represents in the real world
2. Classify every column into a role
3. Classify the time behavior of the dataset
4. Identify possible target variables
5. Infer the real-world domain
6. Identify data health concerns without fixing them
7. Identify misinterpretation risks — columns that could be dangerously misused
8. Write the complete Dataset Identity record to Section 1 of the GAL

---

## 6. Process

### Step 1 — Read the Dataset Structure

DPSU begins by inspecting everything about the dataset's structure: how many rows and columns, what the columns are named, what types of values they hold, how many unique values each column contains, how much data is missing and where.

This is observation only. No interpretation yet. DPSU is collecting the raw material it will reason from.

### Step 2 — Infer Row Meaning

The most critical question DPSU answers is: what does one row represent?

This inference is driven by examining what changes between rows. If a column like "customer_id" repeats many times while a "transaction_date" column changes with each row, the row likely represents a transaction, not a customer. If every row has a unique person identifier and columns like "age" and "income" that don't vary over time, the row likely represents a person profile.

The signals DPSU uses:
- Which columns have unique values (suggests identifiers)
- Which columns repeat frequently (suggests categorical attributes)
- Whether a timestamp column exists and how it relates to entity identifiers
- Whether the same entity appears multiple times (suggests event or panel structure)
- What the column names suggest about their real-world meaning

DPSU must commit to a row meaning interpretation and record it with reasoning. If the interpretation is ambiguous, DPSU records the ambiguity explicitly and states which interpretation it is proceeding with and why.

**Common row types:**
- One transaction or event (each row is one occurrence)
- One entity state (each row is one entity at one point in time)
- One entity summary (each row aggregates an entity's history)
- One time period (each row represents one interval for one entity)

### Step 3 — Classify Column Roles

Every column must be assigned a role. This classification is permanent context that all later modules depend on.

**Identifier** — uniquely identifies an entity and carries no analytical information. Examples: customer_id, order_number, patient_id. Identifiers must never be used as features. This restriction must be recorded.

**Feature** — describes attributes useful for analysis. These are the variables that patterns will be found in.

**Target Candidate** — a column that represents an outcome or result that the analysis might want to predict or explain. DPSU identifies candidates; the user confirms which one matters in QBII.

**Timestamp** — represents when something happened. Time columns require special handling in cleaning, exploration, and feature engineering.

**Categorical Attribute** — represents membership in a category or group. May need encoding for certain analysis types.

**Numeric Measurement** — represents a quantity that can be compared, averaged, or otherwise computed.

**Derived or Redundant Field** — represents information that is already captured in another column, just in a different form. Example: a "full_name" column alongside separate "first_name" and "last_name" columns. These are flagged for careful handling.

Some columns may carry more than one role. A "date" column might be both a timestamp and a feature. DPSU records all applicable roles.

### Step 4 — Classify Time Behavior

The relationship between the dataset and time shapes many downstream decisions. DPSU must classify the dataset into one of four categories.

**Static Snapshot** — each row is independent of time. The dataset captures a state at a single point in time, or time is not relevant to the rows. Cleaning and feature engineering strategies for static snapshots differ from time-aware datasets.

**Time Series** — measurements recorded at regular intervals, typically for one subject or system. The ordering of rows is meaningful. Gaps in time are significant. Forward-fill imputation may be appropriate. Lag features make sense.

**Event Log** — events recorded as they occur, at irregular intervals, possibly for many different entities. The rate of events, the time between events, and sequences of events are all meaningful.

**Panel Data** — the same entities tracked at multiple points in time. Each entity appears multiple times. Both the within-entity change over time and the between-entity differences matter.

If the dataset does not cleanly fit one category, DPSU records the best fit and notes what characteristics deviate from the clean case.

### Step 5 — Identify Target Candidates

A target variable is a column that represents an outcome — something the analysis might want to predict or explain. DPSU identifies candidates based on the following signals:

- Binary or categorical status columns that suggest an end state (churned/not churned, admitted/not admitted, passed/failed)
- Outcome labels that appear to be recorded after other events
- Numeric measurements that represent a result rather than an attribute
- Columns whose name suggests finality or outcome (score, result, status, outcome, flag)

DPSU does not select the final target. It records all plausible candidates and notes what makes each one a candidate. QBII later confirms which one the user actually cares about.

If no target candidates exist, DPSU records this and notes that the analysis type will likely be exploratory, segmentation-based, or monitoring-focused rather than predictive.

### Step 6 — Infer Domain

DPSU infers what real-world domain the dataset belongs to. This matters because domain knowledge shapes what features make sense, what hypotheses are plausible, and what recommendations are actionable.

Domain is inferred from the combination of column names, row meaning, and the types of values present.

**Examples of domains:** healthcare, finance, e-commerce, marketing, human resources, manufacturing, education, logistics, real estate, environmental monitoring.

If the domain is ambiguous between two possibilities, DPSU records both with their respective evidence and notes which it considers more likely.

### Step 7 — Assess Data Health

DPSU performs a non-destructive inspection of data quality. It observes and records. It does not fix.

**What it looks for:**
- Columns with high missing value rates (and whether the missingness is concentrated or distributed)
- Columns where all or nearly all values are identical (low information content)
- Columns with suspicious value ranges (values that fall outside plausible real-world limits)
- Formatting inconsistencies (the same category represented multiple ways)
- Duplicate rows
- Extreme imbalance in categorical columns

These observations are written to the GAL as warnings. DRIL will act on them later.

### Step 8 — Identify Misinterpretation Risks

Some columns are dangerous if misused. DPSU identifies these explicitly so that later modules cannot accidentally misuse them.

**Types of misinterpretation risk:**

*Identifier used as feature* — an ID column that happens to correlate with outcomes (e.g., customer IDs assigned sequentially where older customers behave differently). Using it as a feature produces spurious patterns.

*Post-outcome information* — a column that is only known after the outcome has occurred. Using it as a feature causes data leakage, where the model or analysis uses information it would not have at decision time.

*Encoded target* — a column that is essentially a re-expression of the target variable in a different form. Example: a "churned" column and a "contract_end_reason = voluntary_cancellation" column that means the same thing.

*Aggregated outcome included in a row-level dataset* — a summary statistic computed from outcomes that is then placed back into individual rows.

Each risk is recorded with a clear explanation of what the risk is, why it matters, and what restriction should apply to that column going forward.

---

## 7. Output Written to the GAL

DPSU writes Section 1 — Dataset Identity. This section contains:

- **Dataset Summary** — a plain-language description of what the dataset represents
- **Row Meaning** — what one row represents, with the reasoning behind the interpretation
- **Column Role Map** — every column with its assigned role(s)
- **Time Behavior Classification** — static, time series, event log, or panel, with justification
- **Target Candidates** — a list of possible outcome variables and what makes each a candidate
- **Domain Inference** — the inferred real-world domain with supporting evidence
- **Data Health Warnings** — quality observations, not fixes
- **Misinterpretation Risks** — columns to restrict and why

---

## 8. Failure Handling

**Ambiguous row meaning:** If DPSU cannot determine with confidence what one row represents, it records the two or three most plausible interpretations, explains the evidence for each, selects the most likely one to proceed with, and flags the ambiguity prominently so that later modules and the user are aware.

**Unrecognized domain:** If the domain cannot be inferred from the dataset structure, DPSU records this and defaults to a general analytical approach. Later modules will not be able to apply domain-specific reasoning, and the GAL will reflect this limitation.

**Entirely missing columns or unreadable data:** If the dataset cannot be read or is too incomplete to profile, DPSU records the failure and halts the pipeline. The session cannot proceed without a Dataset Identity record.

**No clear target candidate:** DPSU records this outcome. The pipeline continues; QBII will determine the appropriate analysis type for a dataset without a clear outcome variable.

---

## 9. Operational Rules

1. DPSU is the only module that reads the raw dataset directly. All other modules read from the GAL.
2. No cleaning may occur before DPSU finishes.
3. No features may be engineered without column role classification.
4. No hypotheses may be generated without row meaning.
5. Every column must receive a role classification. No column may be left unclassified.
6. Misinterpretation risks must be recorded before the pipeline proceeds. They are not optional observations.
7. DPSU does not fix data problems. It only records them.

---

## 10. Dependency Map

**Reads from:** Raw dataset only

**Writes to:** GAL Section 1 — Dataset Identity

**Feeds into:**
- QBII (needs domain and row meaning to ask relevant questions)
- DRIL (needs column roles, time behavior, and health warnings to make cleaning decisions)
- EPR (needs domain and row meaning to interpret patterns correctly)
- IHE (needs domain to generate plausible real-world hypotheses)
- FIE (needs column roles and domain to design appropriate features)
- VPE (needs audience type and domain to design appropriate visualizations)
- ADC (needs domain context for KPI selection)
- RG (needs dataset identity to write the opening narrative)
