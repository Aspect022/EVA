# QBII — Question Builder & Intent Inference
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Question Builder & Intent Inference module determines what the user actually wants to accomplish before any data modification or interpretation begins.

A dataset does not have a single correct analysis. The same dataset can be used to predict an outcome, understand a behavior, identify unusual cases, segment a population, or monitor change over time — and each of these goals requires different cleaning decisions, different features, different visualizations, and a different report.

Without knowing the user's goal, EVA cannot make meaningful choices. It can only make generic ones. Generic analysis is almost always wrong for the specific person in front of the system.

QBII exists to make the analysis specific. It translates what the user says — or implies, or fails to say — into a structured analytical intent that every downstream module can act on.

---

## 2. Design Principle

Traditional data tools ask users to configure settings: choose a target variable, select an algorithm, specify an evaluation metric. These are technical questions that most users cannot meaningfully answer. Asking them produces guesses, not intent.

EVA instead conducts a brief, guided conversation using the language of decisions and outcomes, not the language of data science. EVA asks what a thoughtful human analyst would ask a client at the start of an engagement: What are you trying to figure out? What decision will this help you make? Who will use the result?

The module's job is to translate the user's plain-language answers into a structured intent record that the rest of the pipeline can use — without ever asking the user to think like a data scientist.

There is a second, equally important job: inferring intent when the user's answers are incomplete. Not all users will give clear, comprehensive answers. Some will say very little. QBII must be able to proceed even in these cases, using the dataset's structure and domain as context to make reasonable inferences — but it must record those inferences transparently, not proceed as if the user had explicitly confirmed them.

---

## 3. Position in the Pipeline

**Comes after:** DPSU (Stage 0). QBII cannot ask relevant questions without first knowing what kind of dataset it is dealing with.

**Comes before:** DRIL (Stage 2). Cleaning decisions depend on both what the data represents and what the user needs from it.

**Rule:** QBII must read Section 1 of the GAL (Dataset Identity) before generating any questions. Questions that ignore the dataset context reduce trust and waste the user's time.

---

## 4. Inputs

**From the GAL (Section 1 — Dataset Identity):**
- Row meaning (informs what kind of questions make sense)
- Domain (informs what language to use and what goals are plausible)
- Time behavior (determines whether time-oriented questions are relevant)
- Target candidates (determines whether prediction-focused questions make sense)
- Data health summary (informs whether the user should be made aware of significant quality concerns upfront)

**From the user:**
- Responses to the guided question sequence
- Any goal or context the user volunteered before the questions were asked

---

## 5. Core Responsibilities

1. Generate a short, context-aware question sequence (3–5 questions)
2. Ask only questions that make sense given the dataset structure
3. Infer analysis goal from user responses
4. Identify stakeholder type
5. Determine success criteria
6. Confirm the target variable (if applicable) or determine that no target exists
7. Define the interpretability requirement
8. Handle incomplete or ambiguous responses through documented inference
9. Write the complete User Intent record to Section 2 of the GAL

---

## 6. Question Generation

QBII generates 3 to 5 questions. They must be short, decision-focused, and written in plain language. They must never ask the user to make a technical choice.

**The questions are derived from four types:**

**Goal questions** establish what the user is trying to accomplish in the real world.
Examples:
- "What are you trying to figure out from this data?"
- "Are you trying to predict something, understand something, or find unusual cases?"
- "What decision will this analysis help you make?"

**Stakeholder questions** establish who will use the output and how.
Examples:
- "Who will see the results — just you, or will you present them to others?"
- "Do you need to be able to explain the findings to someone non-technical?"

**Priority questions** establish what tradeoffs matter.
Examples:
- "Is it more important to be accurate or to be able to explain why?"
- "Do you need a detailed deep-dive or a clear summary?"

**Time questions** — asked only for time-dependent datasets.
Examples:
- "Are you interested in what has changed over time, or in the current state?"
- "Do you want to understand past patterns or anticipate what happens next?"

**Rules for question generation:**
- Questions must be derived from the GAL. A question about prediction should only appear if target candidates were identified. A question about time trends should only appear if the dataset has time behavior.
- No question may ask the user to choose a statistical method, an algorithm, or a technical parameter.
- If the dataset context makes certain goals clearly impossible, those goals are not offered.

---

## 7. Intent Inference

Based on user responses, QBII infers a structured intent profile.

**Primary Analysis Type** — what kind of analysis is being requested:
- *Prediction* — the user wants to forecast an outcome for future cases
- *Explanation* — the user wants to understand what drives an outcome or behavior
- *Segmentation* — the user wants to identify distinct groups within the data
- *Anomaly Detection* — the user wants to find unusual cases that warrant attention
- *Monitoring* — the user wants to track whether something is changing over time
- *Reporting* — the user wants a clear summary of what the data shows

**Stakeholder Type** — who will use the output:
- *Student* — needs educational clarity; explanations are as important as conclusions
- *Business Owner* — needs actionable direction; implications matter more than methodology
- *Researcher* — needs evidence and rigor; uncertainty and limitations must be surfaced
- *Analyst* — needs depth; can handle complexity and detailed breakdowns
- *Manager* — needs concise summary; decisions are the priority

**Decision Horizon** — the time frame of action:
- *Immediate* — the user needs to act soon based on this analysis
- *Planning* — the user is making medium-term decisions
- *Understanding* — the user is building knowledge without an immediate action in mind

**Interpretability Requirement** — how explainable results need to be:
- *High* — the user must be able to explain every conclusion to others; black-box results are not acceptable
- *Moderate* — some explanation is needed but completeness is not critical
- *Low* — performance or comprehensiveness is the priority; explanation is secondary

**Success Definition** — what outcome makes this analysis useful. This is written in plain language and referenced throughout the analysis to keep EVA oriented toward what actually matters to the user.

---

## 8. Target Confirmation

If DPSU identified one or more target candidates, QBII presents them to the user in plain language and confirms which one the user cares about.

Example: "It looks like this dataset tracks whether customers stayed or left. Is that the main thing you want to understand?"

If the user confirms a target, it is recorded as the selected target in Section 2 of the GAL.

If the user declines all candidates or no candidates exist, QBII records this and sets the analysis type accordingly. Prediction is not forced when no valid outcome variable exists.

---

## 9. Handling Incomplete or Ambiguous Responses

This is one of the most important responsibilities of QBII, and it requires explicit treatment.

Users will not always give clear, complete answers. Some users say very little. Some give answers that point in conflicting directions. Some misunderstand what is being asked. QBII must handle all of these cases without halting the pipeline — but also without silently making assumptions.

**When responses are minimal:**

QBII uses the dataset context (domain, row meaning, target candidates, time behavior) to infer the most likely intent. This inference is recorded in the GAL with full transparency: what the user said, what QBII inferred, and why that inference was made.

The inference follows a conservative hierarchy: if uncertain between explanation and prediction, default to explanation (because explaining is less committal than predicting and more useful when the goal is unclear). If uncertain about stakeholder type, default to a moderately technical audience. If uncertain about interpretability priority, default to high interpretability.

The inferred intent is summarized in plain language and presented to the user for confirmation before the pipeline continues: "Based on what you've told me, it seems like you're trying to understand what drives customer churn, and you'll need to be able to explain the findings to a manager. Does that sound right?"

This confirmation step is not optional when inference is involved. It catches mismatches early, before they propagate through the entire analysis.

**When responses conflict:**

If a user's answers point in two different directions, QBII identifies the conflict explicitly. For example: if the user says they want "very detailed technical analysis" but also says they need to "explain everything to a non-technical audience," those requirements are in tension.

QBII records the conflict in the GAL and resolves it using the priority order: decision clarity first, then interpretability, then complexity. In the example above, it would calibrate toward explainability and note that some technical depth may be traded off.

**When the user corrects EVA's understanding:**

If the user disputes EVA's interpretation of their intent, the correction is recorded in the GAL as an update to Section 2. The original interpretation and the correction are both preserved, with a note explaining what changed and why.

---

## 10. Output Written to the GAL

QBII writes Section 2 — User Intent. This section contains:

- **User Goal** — the primary analytical objective in plain language
- **Analysis Type** — the formal classification (prediction, explanation, segmentation, etc.)
- **Decision Context** — the real-world decision this analysis supports
- **Stakeholder Type** — who will use the results
- **Decision Horizon** — when action will be taken
- **Selected Target** — the confirmed outcome variable, or a note that none was selected
- **Interpretability Requirement** — high, moderate, or low
- **Success Definition** — what makes this analysis useful, in the user's own terms where possible
- **Constraints** — any time, simplicity, or reporting requirements the user identified
- **Inferred Elements** — any parts of the intent profile that were inferred rather than explicitly stated, with the reasoning behind each inference
- **User Confirmation** — whether the user confirmed the inferred intent, and what (if anything) they corrected

---

## 11. Failure Handling

**User provides no answers at all:** QBII infers intent entirely from dataset structure and records this prominently in the GAL. The inferred intent summary is presented to the user before any further processing. If the user does not confirm, EVA pauses and requests a minimal response.

**Dataset context makes all analysis types ambiguous:** QBII defaults to an exploratory analysis goal — discovering what the data contains without a specific prediction target — and records this as a default rather than a confirmed intent.

**Target candidates exist but user cannot identify a relevant one:** QBII records that no target was confirmed and proceeds without one. The analysis type is set to explanation, segmentation, or monitoring as appropriate.

---

## 12. Operational Rules

1. QBII must read Section 1 of the GAL before generating any questions.
2. Questions must never ask technical configuration decisions.
3. Inferred intent must be recorded separately from confirmed intent.
4. Inferred intent must be confirmed by the user before the pipeline continues beyond this stage.
5. No target variable may be forced onto the analysis if the user has not confirmed it.
6. The intent record must be complete before DRIL begins. DRIL's decisions depend on it.

---

## 13. Dependency Map

**Reads from:** GAL Section 1 (Dataset Identity) + user responses

**Writes to:** GAL Section 2 — User Intent

**Feeds into:**
- DRIL (cleaning decisions depend on user goal and selected target)
- EPR (exploration is guided by what the user is looking for)
- FIE (features are designed for the specific analytical objective)
- VPE (visualization complexity is calibrated to stakeholder type)
- ADC (dashboard panels are organized around the decision context)
- RG (report language and depth are calibrated to stakeholder type)
