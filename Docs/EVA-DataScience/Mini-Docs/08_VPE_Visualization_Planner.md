# VPE — Visualization Planner & Executor
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Visualization Planner & Executor converts analytical understanding into visual evidence that a human can see, interpret, and trust.

The module does not generate charts because data is present. It generates charts because specific questions need visual answers. Every visualization EVA produces is the answer to a question that was written down before the chart was created.

The purpose of visualization in EVA is cognitive: to help a human understand a pattern that would otherwise remain abstract, to evaluate whether a hypothesis is consistent with the data, and to communicate findings in a form that is more immediately comprehensible than numbers alone.

---

## 2. Design Principle

Charts are arguments, not decorations.

Typical systems produce charts as a side effect of having data — they generate distributions, scatter plots, and bar charts because those are standard outputs of an analysis pipeline. The charts exist because the data exists.

EVA inverts this. Charts exist because questions exist. Before any visualization is created, the question it will answer is recorded. If the question is not important enough to record, the chart should not be created. If a chart is created but does not clearly answer its intended question, it is rejected.

This principle produces fewer charts — but each one earns its place. A user who sees five meaningful visualizations understands more than a user who sees twenty generic ones.

The second principle: **visualizations must be understandable without statistical training.** The audience for EVA's outputs is not data scientists. A chart that requires understanding of p-values, confidence intervals, or correlation matrices to interpret is not a useful chart for most EVA users. Every visualization must come with an interpretation written in plain language.

---

## 3. Two-Stage Architecture

The VPE is divided into two distinct components that operate sequentially.

**The Visualization Planner** reasons about what to visualize and why. It reads the GAL, selects the most important questions to answer visually, determines the appropriate type of visualization for each question, and records this plan before any chart is created.

**The Visualization Executor** implements what the Planner decided. It creates the charts as specified. It does not independently decide what to visualize. It follows the plan.

This separation is deliberate and important. When planning and execution are combined, the tendency is to create whatever chart is easiest to generate and then reason backward about what question it answers. Separating them forces the harder thinking — about what actually needs to be shown — to happen first.

---

## 4. Position in the Pipeline

**Comes after:** FIE (Stage 5). Visualizations can use derived features, which are often more informative than raw columns.

**Comes before:** ADC (Stage 7). The ADC selects which visualizations to include in the dashboard.

**Rule:** The VPE must read all prior GAL sections before beginning planning. The findings, hypotheses, features, and user context all shape what needs to be visualized.

---

## 5. Inputs

**From the GAL:**
- Section 1 — Dataset Identity (domain, time behavior — determines which chart types are appropriate)
- Section 2 — User Intent (stakeholder type and analytical goal — determines complexity and focus)
- Section 4 — Exploratory Findings (the patterns that need visual illustration)
- Section 5 — Hypotheses (the explanations that need visual evaluation)
- Section 6 — Feature Reasoning (the derived variables that may produce informative visuals)

---

## 6. The Visualization Planner

### Step 1 — Identify What Needs to Be Shown

The Planner reads the exploratory findings and hypotheses in the GAL and identifies which ones would benefit from visual representation.

Not all findings need a chart. Some patterns are clear from a single number. Some are better expressed in a sentence. The Planner selects findings where visual representation genuinely adds understanding — where seeing the pattern makes it clearer than reading about it.

**Findings that typically benefit from visualization:**
- Distributions where the shape matters (skew, bimodality, concentration)
- Relationships between two or more variables where the pattern of the relationship is important
- Group comparisons where the magnitude and direction of differences across groups is the message
- Time trends where the trajectory over time is more important than any single point
- Anomalies where the unusual cases need to be visible relative to the normal cases

### Step 2 — Write the Visualization Question

For every planned chart, the Planner records the specific question the chart will answer. This question is written before the chart is created.

**Examples:**
- "Do customers who churned show lower purchase frequency in the months before churning?"
- "Is the relationship between age and spending linear, or does it plateau at a certain age?"
- "Do the three customer segments identified during exploration differ meaningfully on the key behavioral variables?"
- "Is the Q3 sales decline visible as a discrete drop, or was it a gradual decline across the quarter?"

The question determines: what variables are needed, what type of chart is appropriate, and what the chart should make visually obvious.

### Step 3 — Select the Visualization Type

Chart type selection follows from the question and the nature of the data involved.

**Comparing groups** — when the question is "how do these categories differ?", bar-style comparisons with clear group separation are appropriate. The choice between different bar formats depends on whether the comparison is about absolute values or relative proportions.

**Relationship between variables** — when the question is "how are these two things related?", scatter-style plots that show individual points and overall trend are appropriate. The density and distribution of points matters as much as the overall direction.

**Distribution of a single variable** — when the question is "how is this value spread across the dataset?", histogram or distribution plots show shape, spread, and concentration.

**Change over time** — when the question is "how did this change?", line or area charts that emphasize trajectory and trend are appropriate. Point-in-time bar charts obscure temporal flow.

**Part-to-whole relationships** — when the question is "how does each component contribute to the total?", proportional representations make the relative sizes clear.

**Anomaly detection** — when the question is "where are the unusual cases?", visualizations that show individual points in context of the overall distribution, with anomalies clearly marked, are appropriate.

The Planner records the chosen type and the reason for choosing it.

### Step 4 — Calibrate for Audience

The complexity and annotation level of every visualization is calibrated to the stakeholder type from Section 2 of the GAL.

**Student** — visualizations should be highly annotated, with clear labels explaining what each element shows and why it matters. The chart should teach as well as show.

**Business owner** — visualizations should emphasize the practical implication. What does this pattern mean for a decision? The visual should make the decision point obvious.

**Researcher** — visualizations can show more detail, include reference lines, and be less heavy on annotation. The researcher can read the chart; the annotation should add analytical context, not basic explanation.

**Manager** — visualizations should be clean and summary-level. The key takeaway should be immediately obvious. No chart should require more than a few seconds to understand.

---

## 7. The Visualization Executor

### Creating Charts from the Plan

The Executor takes each planned visualization and creates it according to the Planner's specification. It does not deviate from the plan. If the Executor determines that the specified chart type cannot effectively answer the intended question with the available data, it reports this back to the Planner as a failure rather than substituting a different chart on its own.

Every chart produced by the Executor includes:
- A title that states the question the chart answers, not just what the data shows
- Clear axis labels in plain language
- Annotations that highlight the most important feature of the chart (the specific trend, the key difference, the unusual case)
- A plain-language interpretation — one to three sentences explaining what the chart shows and what conclusion the viewer should draw

### Validation

After each chart is created, the Executor evaluates it against three criteria:

**Does it actually answer the intended question?** Sometimes the data does not produce a clear visual answer. The pattern may be too subtle, the data may be too sparse, or the chosen chart type may not communicate what was intended. If the chart does not clearly answer the question, it fails validation.

**Is it honest about the data?** Charts can mislead through axis manipulation, selective inclusion of data, or visual emphasis on minor differences. The Executor checks that the chart represents the data faithfully.

**Is it understandable without technical knowledge?** If a viewer without data science training cannot understand what the chart is showing within a few seconds of reading the title and annotation, it fails validation.

Charts that fail validation are not shown to the user. The failure is recorded in the GAL, along with the reason. The Planner may revise the plan or acknowledge that the question cannot be effectively answered visually with available data.

---

## 8. Output Written to the GAL

The VPE writes Section 7 — Visualization Plan. For each visualization:

- **Question** — the specific question the visualization answers
- **Related Finding** — the Section 4 entry or Section 5 hypothesis this visualization evaluates
- **Variables Used** — the columns or derived features displayed
- **Chart Type** — the type chosen and the reasoning
- **Audience Calibration** — the stakeholder type this was calibrated for
- **Interpretation** — what the viewer should conclude from this chart
- **Validation Result** — whether the chart passed validation and any notes
- **Confidence Note** — a reminder that visual patterns support conclusions but do not prove causation

---

## 9. Failure Handling

**A planned visualization fails validation:** The failure is recorded in the GAL. The question it was meant to answer is flagged as a question that cannot be effectively answered visually with current data. The ADC and RG are notified so they do not reference a visualization that does not exist.

**The dataset is too small to produce a meaningful visualization:** Some charts require a minimum number of data points to be interpretable. If the dataset is insufficient, the VPE records this and describes the pattern in text rather than producing a misleading chart.

**Conflicting hypotheses produce conflicting visual evidence:** The VPE creates visualizations for each, clearly labeled with which hypothesis each supports. The ADC and RG present them together so the user can see the tension rather than receiving a false resolution.

---

## 10. Operational Rules

1. No visualization may be created without a written question in the Planner's plan.
2. Every visualization must reference a specific finding or hypothesis from the GAL.
3. Every visualization must include a plain-language interpretation written by the Planner.
4. Charts that fail validation are not shown to the user.
5. The Executor may not deviate from the Planner's specification without recording the deviation and its reason.
6. Visualizations must not exaggerate effects through axis manipulation or selective data inclusion.
7. Complexity must be calibrated to the audience — a chart that requires statistical training to read is a failed chart for most EVA users.

---

## 11. Dependency Map

**Reads from:**
- GAL Section 1 — Dataset Identity (domain, time behavior)
- GAL Section 2 — User Intent (stakeholder type, analytical goal)
- GAL Section 4 — Exploratory Findings (patterns to visualize)
- GAL Section 5 — Hypotheses (mechanisms to evaluate visually)
- GAL Section 6 — Feature Reasoning (derived variables available for use)

**Writes to:** GAL Section 7 — Visualization Plan

**Feeds into:**
- ADC (selects which validated visualizations appear in the dashboard)
- RG (embeds selected visualizations in the report narrative)
