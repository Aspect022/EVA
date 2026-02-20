# ADC — Analytical Dashboard Composer
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Analytical Dashboard Composer organizes EVA's findings into a persistent decision interface — a structured workspace that the user can return to repeatedly as their understanding deepens or as new data arrives.

A visualization explains one idea. A dashboard explains a situation.

The dashboard is not a collection of charts assembled for completeness. It is a curated view of the most decision-relevant information, organized to answer the questions a user will ask again and again: what is happening, why is it happening, what needs attention, and what should I do?

---

## 2. Design Principle

The ADC and the Report Generator serve different purposes and should not be confused.

The **Report** is a narrative document — it tells the story of the analysis from beginning to end, for a reader who was not present during the analysis and needs to understand it from scratch. It is generated once and shared. Its value is communication.

The **Dashboard** is a persistent interface — it presents the most important, ongoing-relevance information in a structured form that the user interacts with and returns to. It is designed for someone who already understands the context and needs to stay informed. Its value is awareness.

Both are outputs of EVA. Neither replaces the other. A user who gets both receives a document they can share with others (the report) and a workspace they can use for themselves (the dashboard).

The ADC's guiding design rule: **every element in the dashboard must support an ongoing decision.** If an element would be just as useful to see once in a report as to see repeatedly in a dashboard, it belongs in the report, not the dashboard. The dashboard earns its place by remaining useful over time.

---

## 3. Position in the Pipeline

**Comes after:** VPE (Stage 6). The ADC selects from validated visualizations — it does not create new ones.

**Comes before:** RG (Stage 8). The ADC's selections and recommendations feed the Report Generator's narrative.

**Rule:** The ADC may only include visualizations that passed validation in Section 7 of the GAL. It may not commission new visualizations. If important questions cannot be answered with validated visuals, this limitation is recorded.

---

## 4. Inputs

**From the GAL:**
- Section 1 — Dataset Identity (domain, for KPI selection)
- Section 2 — User Intent (stakeholder type, decision context, analytical goal — shapes which information is most decision-relevant)
- Section 4 — Exploratory Findings (the key patterns that warrant ongoing awareness)
- Section 5 — Hypotheses (the explanations that justify why certain patterns matter)
- Section 6 — Feature Reasoning (derived variables that may serve as KPIs)
- Section 7 — Visualization Plan (the pool of validated visualizations to select from)

The ADC does not access the raw dataset. It works entirely from the GAL.

---

## 5. Core Responsibilities

1. Identify the key performance indicators most relevant to the user's decision context
2. Select the most decision-relevant validated visualizations
3. Organize the selected elements into four logical panels
4. Generate specific, evidence-backed recommendations
5. Calibrate dashboard complexity to the stakeholder type
6. Write the full recommendation set and dashboard plan to the GAL

---

## 6. KPI Selection

Key performance indicators are the metrics the user should monitor to stay informed about the situation the data represents.

KPIs must meet three criteria:
- They directly relate to the user's decision goal (not just to what's interesting in the data)
- They are understandable without statistics knowledge — a number that requires a statistics degree to interpret is not a useful KPI for most EVA users
- They reflect meaningful change — a KPI that never moves or always moves is not useful for decision-making

**KPI selection by domain examples:**

In a customer behavior dataset where the goal is understanding retention, relevant KPIs include the active customer rate, the rate of customers showing early warning signs of churn, and the distribution of customer tenure.

In a healthcare dataset where the goal is identifying at-risk patients, relevant KPIs include the proportion of patients in high-risk categories, the trend in key risk indicators, and the distribution of cases across risk levels.

In an operational dataset where the goal is monitoring quality, relevant KPIs include the rate of anomalous readings, the trend in the primary measurement, and the distribution of outcomes across operating conditions.

For each selected KPI, the ADC records in the GAL: what the KPI is, why it is relevant to the user's decision goal, and what it is derived from.

---

## 7. Dashboard Structure

The dashboard is organized into four logical panels. Each panel answers a specific type of question.

### Panel A — System Overview

**Question answered:** What is currently happening?

This panel provides immediate situational awareness. A user returning to the dashboard after any amount of time should be able to understand the current state of the situation within seconds of looking at this panel.

**Contents:**
- The most important KPIs with current values
- High-level trend indicators (is the situation improving, stable, or deteriorating?)
- A brief plain-language summary of the overall picture

This panel should be readable in under one minute. It is deliberately summary-level.

### Panel B — Drivers & Causes

**Question answered:** Why is this happening?

This panel presents the explanatory layer — the patterns and hypotheses that explain what is observed in Panel A.

**Contents:**
- The validated visualizations that best illustrate the key findings
- The hypotheses from Section 5 of the GAL, presented in plain language
- The most important features or patterns that drive the outcome of interest

This panel builds understanding. It answers "yes, but why?" — the question a user naturally asks after looking at Panel A.

### Panel C — Risk & Alerts

**Question answered:** What needs attention right now?

This panel surfaces urgent items — the cases, trends, or conditions that warrant immediate notice. Not everything in the analysis is equally urgent. This panel is where the most time-sensitive information lives.

**Contents:**
- Anomalies or unusual cases identified during exploration
- High-risk groups or segments identified through pattern analysis
- Trends that are moving in a concerning direction
- Confidence levels for each alert, so the user can calibrate their response

Each alert must be justified by specific GAL evidence. Alerts without evidence are not permitted.

### Panel D — Action Guidance

**Question answered:** What should I do?

This panel is where analysis becomes decision. It presents specific, actionable recommendations based on everything EVA has found and hypothesized.

**Contents:**
- Recommended actions, expressed in plain language
- The specific groups or cases each recommendation applies to
- The expected impact of each action (what improvement is anticipated)
- The urgency level of each action
- The confidence level — how strongly the available evidence supports this recommendation

---

## 8. Generating Recommendations

Recommendations are the most consequential output of the ADC. They convert analysis into action. They must therefore be held to the highest standard of justification.

Every recommendation must satisfy all of the following before it is written:

**Evidence requirement:** The recommendation must be traceable to specific entries in Section 4 (findings) and Section 8 (evidence register) of the GAL.

**Hypothesis requirement:** The recommendation must reference at least one hypothesis from Section 5 of the GAL. A recommendation that is not connected to a proposed mechanism — that says "do X" without explaining why X might work — is not a recommendation, it is a guess.

**Causation discipline:** The recommendation must clearly indicate whether it is based on a strong causal mechanism or a correlational observation. Saying "customers in this group leave at a higher rate; we recommend retaining them" is valid. Saying "if you change X, Y will change" is only valid if the evidence supports a directional relationship.

**Confidence signaling:** Every recommendation carries an explicit confidence level and an honest statement of what would increase or decrease that confidence.

The ADC writes every recommendation to Section 9 of the GAL (Recommendations & Decisions) before it appears in the dashboard.

---

## 9. Stakeholder Adaptation

The dashboard adapts to the stakeholder type established in Section 2 of the GAL.

**Student** — emphasis on explanation and learning. The dashboard includes more annotation and context. It teaches what the KPIs mean, not just what they show.

**Business owner** — emphasis on decision and action. Panel D (Action Guidance) is the most prominent. KPIs are expressed in business terms. Recommendations are specific and actionable.

**Researcher** — emphasis on evidence and nuance. More detail is shown. Uncertainty is surfaced more prominently. The hypothesis panel includes supporting and contradicting evidence.

**Manager** — emphasis on summary and clarity. The dashboard is concise. Only the most important items are shown. Technical detail is available on request but not displayed by default.

---

## 10. Continuity and Comparison

If the user returns to analyze updated data in a subsequent session, the ADC compares the current analysis against the prior one.

It identifies:
- Metrics that have improved since the last session
- Metrics that have deteriorated
- New patterns or anomalies that were not present before
- Recommendations from the prior session and whether the situation they addressed has changed

This comparison is displayed prominently so that the dashboard becomes a monitoring tool — not just a snapshot of one analysis, but an ongoing view of how the situation is evolving.

---

## 11. Output Written to the GAL

The ADC writes Section 9 — Recommendations & Decisions, and records the dashboard plan.

For each recommendation:
- The recommended action in plain language
- The affected group or segment
- The urgency level
- The expected impact
- The confidence level
- The specific GAL entries (findings, hypotheses, evidence) that support it

For the dashboard plan:
- The selected KPIs and their justification
- The selected visualizations and which panel they appear in
- The stakeholder calibration applied

---

## 12. Failure Handling

**No validated visualizations available:** The ADC records this and constructs Panel B from text summaries of findings and hypotheses rather than charts. The absence of visuals is noted prominently.

**Insufficient evidence for recommendations:** If the GAL does not contain enough evidence to support a recommendation at even moderate confidence, the ADC does not generate one. Instead, it records in Panel D what additional information would be needed to make a recommendation. Telling the user "we don't yet have enough to recommend a specific action" is more valuable than a low-confidence recommendation that leads to a bad decision.

**Conflicting hypotheses with equal evidence:** The ADC presents both in Panel B with equal prominence and notes the conflict in Panel C as an item requiring attention — the user should be aware that the explanation is not settled.

---

## 13. Operational Rules

1. The ADC may only include visualizations that passed validation in VPE.
2. Every recommendation must cite specific GAL evidence — it cannot be generated from general reasoning.
3. Every recommendation must reference at least one hypothesis from Section 5.
4. Dashboard elements must not include raw statistical tables by default.
5. Dashboard complexity must be calibrated to the stakeholder type.
6. The ADC must not generate a recommendation when evidence is insufficient — it records the gap instead.
7. Every alert in Panel C must be backed by a GAL entry.

---

## 14. Dependency Map

**Reads from:**
- GAL Section 1 — Dataset Identity
- GAL Section 2 — User Intent
- GAL Section 4 — Exploratory Findings
- GAL Section 5 — Hypotheses
- GAL Section 6 — Feature Reasoning
- GAL Section 7 — Visualization Plan

**Writes to:**
- GAL Section 9 — Recommendations & Decisions
- GAL Dashboard Plan (embedded in Section 9)

**Feeds into:**
- RG (the report narrates what the dashboard shows and the reasoning behind its recommendations)
