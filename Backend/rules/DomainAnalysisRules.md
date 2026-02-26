# Domain Analysis Rules

These rules dictate how EVA's Dataset Profiler & Semantic Understanding (DPSU) module infers the domain of a given dataset.

## Core Objective
Analyze the statistical summary of the dataset and infer its real-world identity. Establish the fundamental ground truth of what this dataset represents.

## Rules
1. **Domain Identification:** Determine the broad industry or field (e.g., Healthcare, E-commerce, Finance, Operations, HR). Look at column names like `patient_id` vs `transaction_amount` to make an educated guess.
2. **Row Semantics:** Clearly define what a single row represents. Is it a unique customer? A single transaction? A daily aggregate? A specific event in time?
3. **Temporal Behavior:** Classify the time behavior of the dataset. Is it a static snapshot (no time columns), a time series (regularly spaced intervals), an event log (timestamps for discrete events), or panel data (multiple entities over time)?
4. **Column Roles:** Assign a role to every column:
    *   `identifier`: Primary keys, IDs, names.
    *   `target_candidate`: Variables that are commonly predicted (e.g., `churn`, `price`, `fraud`, `status`).
    *   `feature`: Attributes used for analysis.
    *   `metadata`: Timestamps, flags, or data collection hints.
5. **Quality Observations:** Note missing values or apparent type mismatches as health observations. Do not attempt to fix them; simply document their existence.
6. **Misinterpretation Risks:** Highlight columns that might be confusing or easily misused (e.g., an ID column stored as an integer that might accidentally be used in math).

## Output Requirement
The output must STRICTLY align with the `DatasetIdentity` schema in the Global Analysis Ledger (GAL).
