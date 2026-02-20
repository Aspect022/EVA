# GAL — Global Analysis Ledger
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. What the GAL Is

The Global Analysis Ledger is the permanent shared reasoning record of an EVA analysis session. It is the single source of truth that every module reads from and writes to throughout the entire pipeline.

The GAL is not a log file. A log records what happened. The GAL records what was understood, decided, discovered, and concluded — and why. Every entry is a reasoned statement, not an event record.

The GAL is not a cache. A cache holds temporary data for performance purposes. The GAL holds permanent reasoning that must remain available, intact, and traceable for the lifetime of the session and beyond.

The GAL is the official reasoning record of the analysis. If a conclusion appears in EVA's output, it must be traceable to an entry in the GAL. If something is not in the GAL, it did not happen as far as EVA is concerned.

Think of it as the structured notebook a careful human analyst keeps while working — except every page is written in a consistent format, every claim cites its source, and every decision records the alternatives that were considered and rejected.

---

## 2. Why the GAL Exists

The fundamental failure mode of automated data pipelines is lost reasoning context.

A cleaning stage removes a column. A feature engineering stage needed it. A model produces biased results. Nobody knows why, because the cleaning decision was never recorded with its reasoning — only its effect.

This is not a fringe problem. It is the default failure mode of systems where each stage works in isolation. The stages may individually be correct, but the system as a whole loses coherence because there is no shared memory of why things were done.

The GAL solves this by making reasoning explicit, persistent, and shared. Every module that makes a decision records what it decided, why it decided it, what alternatives it considered, and what effect the decision had. Every later module that depends on that decision can look it up, understand it, and act consistently with it.

The GAL guarantees:

**Continuity** — each stage knows everything that came before it.

**Explainability** — every conclusion has a traceable chain of reasoning.

**Reproducibility** — the full analysis can be reconstructed from the GAL alone.

**Consistency** — no module can accidentally contradict a prior decision without acknowledging it.

**Trust** — the user can ask "why did EVA do this?" and receive a real answer.

---

## 3. The Append-Only Principle

The GAL operates on a strict append-only principle. This is one of the most important rules in the entire EVA system.

Once an entry is written to the GAL, it cannot be deleted or overwritten. It can only be annotated or superseded by a new entry that explicitly references the original.

This rule exists for three reasons.

First, reproducibility. If earlier reasoning can be overwritten, there is no way to reconstruct what the system believed at any point in time or why it made a particular decision.

Second, accountability. If a later module discovers that an earlier assumption was wrong, that discovery is itself important information. It should be recorded as a correction, not hidden as an overwrite.

Third, trust. A system that modifies its own past reasoning without a trace is a system that cannot be audited. EVA must be auditable.

**What append-only means in practice:**

When a module confirms an earlier entry, it adds a confirmation note referencing the original entry.

When a module extends an earlier entry with new information, it adds a new entry in the appropriate section that explicitly states what it is building on.

When a module discovers that an earlier entry was wrong or incomplete, it adds a correction entry that identifies the original entry, explains what was incorrect, explains what is now understood to be true, and records what effect this correction has on the analysis going forward.

The original entry remains visible. The correction is added alongside it. Any reader can see both the original reasoning and the correction — and understand why the change was made.

---

## 4. Contradiction Handling

Because the GAL is written by multiple modules across time, contradictions can and will occur. A later module may discover something that conflicts with what an earlier module recorded. The GAL has a defined process for handling this.

**Step 1 — Identify the conflict.** The later module notes that its finding conflicts with an existing GAL entry. It records which entry is in conflict and what specifically conflicts.

**Step 2 — Assess the impact.** The module records what effect this conflict has on the analysis. Does it change a cleaning decision that was already made? Does it affect a hypothesis that was already formed? The impact must be explicitly assessed, not left implicit.

**Step 3 — Record the resolution.** The module records how the conflict is resolved and why. Resolution options include: the new information supersedes the old (with explanation of why), the new information does not actually conflict on closer examination (with explanation of why), or the conflict is genuine and unresolved (in which case it is flagged as an open question and both interpretations are carried forward with explicit uncertainty).

**Step 4 — Propagate the correction.** If the resolution changes something that downstream modules have already acted on, the GAL records which downstream outputs may now be affected. This creates a visible audit trail of cascading changes.

The key rule: no contradiction is ever silently resolved. Every conflict is visible in the GAL.

---

## 5. Structure of the GAL

The GAL is organized into ten sections. Each section corresponds to a specific stage of the pipeline and is owned by the module that runs at that stage. Sections are populated sequentially as the pipeline progresses.

---

### Section 1 — Dataset Identity
**Written by:** Dataset Profiler & Semantic Understanding (DPSU)

This section establishes what the data is. It is the reference reality for the entire session. Every later module consults this section before acting. No module may make decisions that contradict this section without explicitly recording an update with justification.

**Contains:**
- What the dataset represents in the real world
- What one row means (one transaction, one patient visit, one sensor reading, etc.)
- How the data behaves over time (static snapshot, time series, event log, panel data)
- The inferred real-world domain
- The role of every column (identifier, feature, target candidate, timestamp, categorical attribute, numeric measurement, derived or redundant field)
- Possible target variables
- Data health observations (quality issues noted, not fixed)
- Misinterpretation risks (columns that could be misused and why)

---

### Section 2 — User Intent
**Written by:** Question Builder & Intent Inference (QBII)

This section establishes what the user wants. It is the objective context for the entire session. Cleaning decisions, feature choices, visualization complexity, and report tone all depend on this section.

**Contains:**
- The user's primary analytical goal (prediction, explanation, segmentation, anomaly detection, monitoring, or reporting)
- The real-world decision the analysis is meant to support
- The stakeholder type (student, business owner, researcher, analyst, manager)
- The selected target variable (if applicable) or the reason no target was selected
- Interpretability priority (how important is it that results be explainable vs. just accurate)
- Success definition (what outcome makes this analysis useful)
- Constraints (time, simplicity, reporting requirements)
- Inferred intent (if the user's answers were minimal, what EVA inferred and why)

---

### Section 3 — Data Integrity Record
**Written by:** Data Repair & Integrity Layer (DRIL)

This section documents every modification made to the dataset. No change to the data is permitted without a corresponding entry here. This section is the proof that the cleaned dataset is trustworthy.

**Contains, for each modification:**
- The problem that was detected
- Why it matters for this specific analysis
- The strategy chosen to address it
- The alternatives that were considered and why they were rejected
- The effect on the dataset (rows affected, columns changed, etc.)
- The confidence level that the chosen strategy was correct
- Any residual risk introduced by the choice

**Also contains:**
- Columns flagged as restricted (not to be used as features) and why
- The final validation result confirming the repaired dataset still represents the original process

---

### Section 4 — Exploratory Findings
**Written by:** Exploration & Pattern Recognition (EPR)

This section records what patterns actually exist in the data. It contains observations only — not explanations, not recommendations, not hypotheses. Those come later. This section is purely the evidence layer.

**Contains:**
- Distribution characteristics of key variables
- Correlations between variables and their strength
- Detected segments or natural groupings
- Anomalies and unusual observations
- Temporal trends (for time-dependent datasets)
- Behavioral differences between groups
- Variables most associated with the target (if a target exists)

The discipline of this section is deliberate. By recording observations separately from explanations, EVA ensures that later hypotheses are grounded in actual findings rather than assumptions — and that the distinction between "what we found" and "what we think it means" remains clear to the user.

---

### Section 5 — Hypotheses
**Written by:** Investigation & Hypothesis Engine (IHE)

This section records proposed real-world explanations for the patterns found in Section 4. It is the reasoning layer — the step that converts pattern detection into understanding.

**Contains, for each hypothesis:**
- The specific observation from Section 4 that this hypothesis attempts to explain
- The proposed real-world mechanism (expressed in domain language, not statistical language)
- Supporting evidence from the dataset
- Contradicting evidence from the dataset (if any)
- A plausibility assessment (high, moderate, or low) with reasoning
- A confidence note acknowledging the limits of the available evidence

**Rules for this section:**
- Every hypothesis must reference a specific observation from Section 4
- At least two hypotheses must be generated for each significant observation, unless evidence is overwhelmingly concentrated on one explanation
- No hypothesis may be labeled as proven or certain
- Hypotheses from this section are what downstream modules cite when making recommendations

---

### Section 6 — Feature Reasoning
**Written by:** Feature Intelligence Engine (FIE)

This section records every derived feature that EVA proposes creating. Features are not created silently — every proposed variable is justified in terms of both its statistical purpose and its real-world meaning.

**Contains, for each proposed feature:**
- The name of the feature
- Which raw columns it is derived from
- The real-world meaning of the feature (what it represents about the domain)
- The statistical purpose (what information it captures that the raw columns do not)
- The hypothesis or observation that motivated it
- The expected impact on analysis quality
- Any limitations or risks of using this feature

---

### Section 7 — Visualization Plan
**Written by:** Visualization Planner & Executor (VPE)

This section records the reasoning behind every visualization EVA creates. A chart without a question is decoration. This section ensures every chart answers a specific, recorded question.

**Contains, for each visualization:**
- The question the visualization is designed to answer
- The finding or hypothesis it is evaluating
- The audience it is designed for
- The type of visualization chosen and why
- The interpretation — what the user should understand from seeing it
- A confidence note reminding the user that visual evidence supports conclusions but does not prove them

---

### Section 8 — Evidence Register
**Written by:** All modules, maintained throughout the session

This is the citation index of the analysis. Every conclusion EVA produces must have an entry here. The Evidence Register maps each conclusion to the specific observations, hypotheses, features, and statistics that support it.

Think of it as the footnotes of a research paper. Before EVA can claim something, it must be able to cite it here.

**Contains, for each conclusion:**
- The conclusion being made
- The specific GAL entries that support it (section and entry reference)
- The strength of the evidence (strong, moderate, or weak)
- Any gaps in the evidence — what would make the conclusion stronger

**Rule:** If EVA cannot populate an Evidence Register entry for a conclusion, that conclusion cannot be stated. This rule applies everywhere — in the dashboard, in the report, in conversational responses.

---

### Section 9 — Recommendations & Decisions
**Written by:** Analytical Dashboard Composer (ADC)

This section records the specific actions EVA recommends the user consider, based on everything discovered and hypothesized.

**Contains, for each recommendation:**
- The recommended action
- The affected group or segment (who this recommendation applies to)
- The urgency level
- The expected impact
- The confidence level
- The specific hypotheses and evidence entries that justify this recommendation

**Rule:** No recommendation may appear here without citing Section 5 (hypotheses) and Section 8 (evidence). Recommendations without evidence are not permitted.

---

### Section 10 — Report Memory
**Written by:** Report Generator (RG)

This section stores the final narrative and the record of what was communicated to the user.

**Contains:**
- The final report narrative
- Which GAL entries were cited in the report
- Which visualizations were included
- Which recommendations were communicated
- The audience level the report was calibrated for

This section allows the report to be regenerated later — even in a new session — because the full reasoning record is preserved here.

---

## 6. GAL Integrity Rules

These rules govern the GAL as a system. They apply to all modules without exception.

**No module may skip reading the GAL before acting.** Every module must consult all prior sections before taking any action. Acting on stale or incomplete context is equivalent to working in isolation — the failure mode the GAL is designed to prevent.

**No module may write to the GAL without justification.** Every entry must explain why it was made, not just what it says.

**No module may silently modify data.** Any change to the dataset must have a corresponding entry in Section 3. There are no exceptions.

**Every claim must cite ledger evidence.** If it cannot be cited, it cannot be claimed.

**Hypotheses must precede recommendations.** Section 5 must exist before Section 9 can be written. Recommendations without hypotheses are guesses, not analysis.

**The GAL must be sufficient to reproduce the analysis.** If someone reads the full GAL and re-runs the pipeline from scratch, they should arrive at the same conclusions. If the GAL does not contain enough information to make this possible, entries are incomplete.

---

## 7. The GAL Across Sessions

A GAL is created when a session begins and is preserved when a session ends. If a user returns to analyze an updated version of the same dataset, the previous GAL is available for comparison.

The returning session creates a new GAL for the new analysis but can reference entries from the previous session. This allows EVA to identify what has changed, what has improved, and what new questions have emerged — and to present these changes clearly rather than treating each session as if it were the first.

This is how EVA becomes a monitoring tool over time, not just a one-time analysis assistant.
