# IHE — Investigation & Hypothesis Engine
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Investigation & Hypothesis Engine transforms observed data patterns into possible real-world explanations.

Exploratory analysis identifies what is happening in the data. The IHE asks why it might be happening in the real world.

This distinction is the difference between a reporting tool and a reasoning system. Without the IHE, EVA can tell a user that customers who haven't purchased in 60 days are more likely to leave. With the IHE, EVA can propose that this might be because they found an alternative, because they had a bad experience that wasn't captured in the data, or because their needs changed and the product no longer serves them. These are different explanations that suggest different actions.

The IHE does not find the answer. It generates structured, plausible explanations that can be evaluated against available evidence and used to guide decisions. It converts pattern detection into understanding.

---

## 2. Design Principle

The governing rule of the IHE is this: **correlation is not explanation.**

When exploratory analysis finds a relationship between two variables, that relationship does not automatically imply a cause. A relationship says "these things tend to occur together." It does not say "one causes the other," "both are caused by a third thing," or "this is a meaningful relationship at all."

The IHE exists to interpret relationships carefully and responsibly. It proposes mechanisms — real-world processes that could plausibly produce the observed pattern — and evaluates how well the available data supports each one.

It never claims to have found the truth. It claims to have found plausible candidates for the truth, ranked by how well they fit the evidence.

A second important principle: **single-explanation outputs are a failure mode.** Reality is almost always more complex than one cause. When only one explanation is offered, the user is nudged toward treating it as fact. When multiple explanations are offered, the user is reminded that the data supports possibilities, not certainties. Multiple hypotheses are not a sign of uncertainty — they are a sign of intellectual honesty.

---

## 3. Position in the Pipeline

**Comes after:** EPR (Stage 3). The IHE cannot generate hypotheses without observations to explain.

**Comes before:** FIE (Stage 5), VPE (Stage 6), ADC (Stage 7), RG (Stage 8). All of these depend on the IHE's hypotheses to explain and justify their outputs.

**Rule:** The IHE must read Section 4 (Exploratory Findings) and all prior GAL sections before generating any hypotheses. Domain context, row meaning, user intent, and data quality limitations all shape what hypotheses are plausible.

---

## 4. Inputs

**From the GAL:**
- Section 1 — Dataset Identity (domain, row meaning, time behavior — essential for generating domain-relevant hypotheses)
- Section 2 — User Intent (analytical goal — determines which observations are most important to explain)
- Section 3 — Data Integrity Record (data limitations — constrains the confidence of hypotheses)
- Section 4 — Exploratory Findings (the observations to be explained)

The IHE reads observed patterns, not raw data. It reasons from interpreted findings, not from numbers. This is intentional — the IHE is a reasoning module, not a computational one.

---

## 5. Core Responsibilities

1. Identify which exploratory findings are significant enough to warrant explanation
2. For each significant finding, generate multiple plausible real-world explanations
3. Evaluate each explanation against available evidence in the dataset
4. Assign a plausibility level with reasoning
5. Record uncertainty honestly
6. Write all hypotheses to Section 5 of the GAL

---

## 6. What Counts as a Significant Finding

Not every observation in Section 4 requires hypothesis generation. Minor statistical noise does not warrant it. The IHE selects findings that are:

- Strong correlations between variables that are likely to matter for the user's goal
- Sudden or unexpected changes in trends over time
- Highly skewed distributions that suggest an unusual underlying process
- Meaningful differences between segments or groups
- Variables that emerge as strongly associated with the target
- Outliers or anomalies that are real rather than noise
- Behavioral differences between groups that are not easily explained by chance

The selection is guided by the user intent. A finding that is statistically interesting but irrelevant to the user's actual decision receives lower priority than a finding that directly bears on what the user is trying to accomplish.

---

## 7. Hypothesis Generation Process

For each selected observation, the IHE follows five steps.

### Step 1 — Translate the Observation into Plain Language

Statistical output is first converted into a real-world statement.

Not: "Variable X shows a Pearson correlation of 0.67 with variable Y."
But: "Customers who have not made a purchase in more than 60 days are significantly more likely to have left the service."

This translation is necessary because hypotheses must be about the real world, not about the data. The data is evidence about reality; hypotheses are about reality itself.

### Step 2 — Read the Domain Context

The IHE consults the dataset identity and domain to understand what the observation could represent in the real world.

The same pattern carries different meaning in different domains. Inactivity in an e-commerce dataset suggests disengagement. Inactivity in a healthcare dataset suggests missed follow-up appointments, which could indicate recovery, dropout, or deterioration. Inactivity in an educational platform might mean the student completed the course, abandoned it, or switched platforms.

Without domain context, hypothesis generation produces generic, unhelpful explanations. With domain context, it produces explanations a domain expert would recognize as plausible.

### Step 3 — Generate Candidate Explanations

The IHE produces multiple possible causes for each observation. Each candidate must be:

- A real-world mechanism, not a statistical statement
- Expressed in domain language
- Specific enough to suggest what additional evidence would support or refute it
- Plausible given the domain context established by DPSU

**The minimum is two candidates for every significant observation.** If the evidence is so concentrated that only one explanation seems remotely plausible, the IHE still records the most viable alternative, even if its plausibility is low. Single-explanation outputs are not permitted.

**Example:**

Observation: Sales declined sharply in Q3.

Candidates:
1. Seasonal demand shift — the product category experiences lower demand in Q3 due to seasonal purchasing patterns.
2. Price change effect — a price increase in Q3 reduced purchase volume.
3. Competitor entry — a competing product entered the market and captured some share.
4. Product availability issue — stock limitations in Q3 reduced the ability to fulfill demand.
5. Customer retention failure — existing customers did not return as expected.

### Step 4 — Evidence Matching

For each candidate hypothesis, the IHE searches the available dataset for evidence that supports or contradicts it.

**Supporting evidence:** data patterns consistent with the hypothesis. If the hypothesis is "seasonal demand shift," supporting evidence might be that the same Q3 decline appears in prior years, or that categories associated with summer peaks are similarly affected.

**Contradicting evidence:** data patterns inconsistent with the hypothesis. If the hypothesis is "price change effect" but no price change is recorded in the dataset and the decline is uniform across price tiers, that is contradicting evidence.

**Missing evidence:** information that would be needed to properly evaluate the hypothesis but is not present in the dataset. This must be recorded explicitly. A hypothesis that cannot be evaluated from available data is not worthless — it may still be plausible — but its plausibility is lower because it cannot be confirmed.

**Rule:** A hypothesis may remain plausible even with weak evidence, but contradicting evidence must reduce its plausibility level. The IHE does not ignore evidence that weakens a hypothesis.

### Step 5 — Assign Plausibility

Each hypothesis receives one of three plausibility levels.

**High Plausibility** — the dataset contains meaningful evidence that supports this explanation, and no significant evidence contradicts it. The mechanism is consistent with the domain context.

**Moderate Plausibility** — the dataset contains some consistent evidence but it is not strong enough to be convincing on its own. The mechanism is plausible in the domain but the data does not clearly confirm it.

**Low Plausibility** — the dataset contains limited or conflicting evidence, or the mechanism is less consistent with the domain context. The explanation is worth noting but should not drive decisions on its own.

**What these levels do not mean:** High plausibility does not mean the hypothesis is true. Low plausibility does not mean the hypothesis is false. They are assessments of how well the available evidence fits the proposed explanation. Reality may differ from what the data shows.

---

## 8. Output Written to the GAL

The IHE writes Section 5 — Hypotheses. Each entry contains:

- **Observation** — the specific finding from Section 4 that this hypothesis explains, referenced by its entry
- **Hypothesis** — the proposed real-world mechanism in plain domain language
- **Supporting Evidence** — specific data patterns from the dataset that are consistent with this hypothesis
- **Contradicting Evidence** — specific data patterns that are inconsistent, or a note that no contradicting evidence was found
- **Missing Evidence** — what information would be needed to evaluate this more rigorously
- **Plausibility Level** — High, Moderate, or Low
- **Reasoning** — why the plausibility level was assigned, tying together the evidence
- **Confidence Note** — an honest statement about the limits of this assessment, including what cannot be determined from the data alone

---

## 9. Failure Handling

**An observation has no plausible real-world explanation:** This is itself an important finding. It suggests the pattern may be a data artifact rather than a real-world signal. The IHE records this assessment and flags the observation for the user's attention. It does not invent explanations to fill the space.

**Domain context is ambiguous and hypotheses are hard to generate:** The IHE generates more general hypotheses based on the pattern type (trend change, segment difference, strong correlation) rather than domain-specific ones. It flags in the GAL that domain-specific reasoning was limited by ambiguity in the domain classification.

**Evidence is entirely absent from the dataset for all candidates:** The IHE records all candidates at low plausibility, notes that the dataset does not contain evidence to distinguish between them, and identifies what additional data would be needed. This is honest and useful — it tells the user what they cannot conclude from their current data.

---

## 10. Operational Rules

1. The IHE must not invent data or patterns that are not present in the dataset or Section 4 of the GAL.
2. The IHE must not claim causation as established fact.
3. Every hypothesis must be linked to a specific observation in Section 4.
4. At least two hypotheses must be generated for each significant observation unless evidence is overwhelmingly concentrated (and even then, the most viable alternative must be recorded).
5. Contradicting evidence must be recorded. It may not be omitted to make a hypothesis look stronger.
6. Domain-irrelevant explanations must not be included. Every hypothesis must be plausible in the context established by DPSU.
7. Plausibility levels are assigned based on evidence, not on what seems like the most satisfying answer.

---

## 11. Dependency Map

**Reads from:**
- GAL Section 1 — Dataset Identity (domain, row meaning, time behavior)
- GAL Section 2 — User Intent (which observations are most important to explain)
- GAL Section 3 — Data Integrity Record (data limitations that constrain hypothesis confidence)
- GAL Section 4 — Exploratory Findings (the observations to be explained)

**Writes to:** GAL Section 5 — Hypotheses

**Feeds into:**
- FIE (features are designed to test or capture the mechanisms identified in hypotheses)
- VPE (visualizations are chosen to evaluate specific hypotheses)
- ADC (dashboard panels explain what is happening and why, citing hypotheses)
- RG (the report explains findings in terms of hypotheses and evidence)
- GAL Section 9 — Recommendations (all recommendations must cite hypotheses from this section)
