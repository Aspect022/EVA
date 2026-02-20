# RG — Report Generator
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Report Generator converts EVA's complete reasoning record into a structured, human-readable narrative document that can be read, understood, and shared by someone who was not present during the analysis.

The report is not a data export. It is not a chart summary. It is not a list of findings. It is a narrative — a story that explains what the data is, what was discovered, why it might be happening, what uncertainty remains, and what the reader should consider doing.

The report serves a specific purpose that the dashboard does not: communication with others. The dashboard is for the user who conducted the analysis. The report is for everyone they need to bring along with them — a manager, a client, a professor, a colleague, a decision-maker who was not in the room.

---

## 2. Design Principle

Data analysis is only valuable if it can be communicated. A correct analysis that cannot be explained to the people who need to act on it produces no value in the world.

The Report Generator performs translation, not computation. It takes technical reasoning and converts it into understandable language. It takes structured GAL entries and converts them into a flowing narrative. It takes uncertainty that is recorded precisely and expresses it honestly in plain terms.

Three rules govern this translation:

**Truthful to the analysis.** The report must not distort, simplify, or omit findings in ways that change their meaning. Every claim in the report must trace to a GAL entry. If the analysis is uncertain, the report must say so.

**Understandable to a non-technical reader.** The report must not require statistical knowledge to read. It may mention that patterns exist, that relationships were found, that confidence is moderate — but it does not expose the reader to methods, metrics, or jargon that they need specialized training to interpret.

**Clearly separates observation from explanation.** Throughout the report, the distinction between "what was found" and "what might explain it" must be visible to the reader. A finding is what was observed in the data. A hypothesis is a proposed explanation. These are different things, and the reader must be able to tell them apart.

---

## 3. The ADC–RG Relationship

The ADC and the RG are distinct outputs for distinct purposes. Understanding the relationship between them is essential to understanding both.

**The ADC produces a persistent interface.** It is designed for ongoing use. The user returns to it. It monitors change. It surfaces alerts. It lives in the product.

**The RG produces a one-time document.** It is designed to be read linearly from start to finish by someone who is learning about the analysis for the first time. It is generated on demand and then exists as a standalone artifact.

The ADC feeds the RG. The selections the ADC made — the KPIs, the visualizations it included in each panel, the recommendations it generated — are inputs to the RG's narrative. The RG explains the reasoning behind those decisions in prose form.

The RG does not feed the ADC. The report is a downstream output; it does not change what the dashboard contains.

---

## 4. Position in the Pipeline

**Comes after:** ADC (Stage 7). The RG reads from the complete GAL, which is fully populated only after all prior modules have run.

**Rule:** The RG performs no new analysis. It reads the GAL and translates. If a conclusion does not appear in the GAL, it does not appear in the report. If the GAL expresses uncertainty, the report expresses uncertainty.

---

## 5. Inputs

**From the GAL — all sections:**
- Section 1 — Dataset Identity (the foundation of the report's opening)
- Section 2 — User Intent (the stakeholder type that determines language and depth)
- Section 3 — Data Integrity Record (the cleaning narrative)
- Section 4 — Exploratory Findings (the key patterns)
- Section 5 — Hypotheses (the proposed explanations)
- Section 6 — Feature Reasoning (the variables that were created)
- Section 7 — Visualization Plan (the validated charts to embed)
- Section 8 — Evidence Register (the citations for every claim)
- Section 9 — Recommendations (the actions to communicate)

The RG reads the entire GAL. It is the only module that needs to.

---

## 6. Report Structure

The report follows a consistent structure with eight sections. Each section has a defined purpose and a defined source in the GAL.

### A. Executive Summary

A short overview — readable in under two minutes — that tells the reader the three most important things:

1. What was analyzed (one or two sentences on the dataset)
2. What was discovered (the two or three most important findings)
3. What it means (the key recommendation or decision implication)

The executive summary must stand alone. A busy reader who reads only this section should understand what was found and what it suggests they should do. They may not have the full picture, but they should have enough to know whether they need to read further.

### B. What the Data Represents

A plain-language explanation of the dataset — what it is, what each row means, what process produced it, and what domain it belongs to.

This section builds the reader's confidence that the analysis is grounded in reality. A reader who does not trust that the analyst understood the data will not trust the findings. This section earns that trust by demonstrating understanding before presenting conclusions.

Sources: GAL Section 1.

### C. How the Data Was Prepared

A summary of the Data Repair & Integrity Layer's work — what problems were found, what was done about them, and why the cleaned data can be trusted.

This section is not a technical audit. It is a confidence statement. It tells the reader: the data had imperfections, they were handled carefully and transparently, and here is how the decisions were made. The reader does not need to understand the statistical details — they need to understand that the process was thoughtful.

It also communicates limitations honestly. If a column had significant missing data that could not be fully resolved, the report says so and notes what this means for interpreting the findings.

Sources: GAL Section 3.

### D. What Was Found

The main findings of the exploratory analysis, presented as clear, plain-language observations.

This section contains observations only — no explanations, no recommendations. It presents the evidence before the interpretation, which mirrors the actual analytical process and helps the reader evaluate the later hypotheses with their own judgment.

Each finding should be a statement that a reader can evaluate as true or false from the data. Not "customers seem to churn a lot" but "customers who have not purchased in more than 60 days leave at a rate three times higher than active customers." Specific. Concrete. Observable.

Sources: GAL Section 4.

### E. Why It Might Be Happening

The Investigation & Hypothesis Engine's work, translated into narrative form.

This section is explicitly framed as explanation, not fact. The language throughout uses "may," "might," "suggests," and "is consistent with" rather than "is" or "causes." The reader must understand that EVA is proposing plausible explanations, not establishing causes.

For each major finding in Section D, this section presents the most plausible hypothesis, briefly describes the supporting evidence, and — importantly — acknowledges what the data cannot tell us. If there is a competing hypothesis that cannot be ruled out, it is mentioned.

The goal is to give the reader a way of thinking about why the patterns exist, not to tell them definitively why they exist.

Sources: GAL Section 5.

### F. Visual Evidence

The validated visualizations selected by the ADC, embedded in the report with interpretations.

Every chart in this section appears with:
- A title that states what the chart is showing
- A plain-language caption that explains what the reader should notice and what it means
- A note connecting it to the finding or hypothesis it supports

No chart appears without its interpretation. A chart without an interpretation asks the reader to do analytical work that the report should have done for them.

Sources: GAL Section 7 (validated visualizations), GAL Section 8 (evidence register).

### G. What to Consider Doing

The recommendations from the ADC, presented in the language of suggestion and consideration rather than instruction.

Each recommendation includes:
- The specific action or direction suggested
- Who it applies to (the affected group or segment)
- Why it is suggested (the evidence and hypothesis that support it)
- How confident EVA is in this recommendation
- What would change the recommendation (what additional information would make it stronger or weaker)

The language in this section is careful about causation. Where the evidence supports a directional relationship, the report says so. Where it does not, recommendations are framed as "consider" and "explore" rather than "do" and "implement."

Sources: GAL Section 9.

### H. Limitations and Confidence

An honest accounting of what EVA does not know, what the data cannot tell us, and where the reader should apply extra caution.

This section is not a disclaimer added to protect EVA from being wrong. It is a substantive part of the report that increases the reader's ability to use the findings wisely. A reader who understands the limitations is in a much better position to act appropriately than one who receives only confident-sounding conclusions.

**What this section covers:**
- Data quality limitations that could affect specific findings (a heavily imputed column, a known selection bias, a restricted column that limited the analysis)
- Hypotheses that are plausible but unconfirmed, and what would be needed to confirm them
- Recommendations where the evidence is moderate rather than strong
- What types of data or additional analysis would strengthen the conclusions

Sources: GAL Sections 3, 5, and 8 (evidence gaps).

---

## 7. Audience Adaptation

The same GAL content produces a different report depending on the stakeholder type from Section 2.

**Student** — the report explains its reasoning step by step. It connects findings to methods in enough detail that the student understands why each analytical choice was made. It has an educational register without being condescending.

**Business owner** — the report is action-oriented. Sections G (recommendations) and H (limitations) are prominent. Findings and hypotheses are concise. The emphasis is on "what this means for your decisions" rather than "what we found in the data."

**Researcher** — the report is detailed and precise. It surfaces nuance, presents competing hypotheses, and is explicit about the strength of evidence for each conclusion. Section H is extensive.

**Manager** — the report is concise. Executive Summary and What to Consider Doing are the most substantial sections. The rest exists to support those two.

The adaptation does not change the conclusions. It changes the depth, the language register, the emphasis, and the ordering of what is most prominent.

---

## 8. Output Written to the GAL

The RG writes Section 10 — Report Memory, containing:

- The complete report narrative
- Which GAL entries were cited in the report (by section and entry)
- Which visualizations were included
- Which recommendations were communicated
- The stakeholder calibration applied
- The date of generation

This record allows the report to be regenerated later — even after the session has closed — because all the reasoning is preserved.

---

## 9. Failure Handling

**A key GAL section is incomplete:** The report notes the gap explicitly in the relevant section. It does not speculate beyond what the GAL contains. If findings are incomplete because exploration was limited, the report says so.

**Findings and hypotheses conflict:** The report presents the conflict honestly in Sections D and E. It does not choose a winner. It tells the reader that the evidence points in different directions and what would be needed to resolve the conflict.

**No recommendations could be generated by the ADC:** Section G states clearly that the available evidence did not support specific recommendations, and explains what additional data or analysis would change this. A report without recommendations is not a failed report — it is an honest one.

---

## 10. Operational Rules

1. The RG performs no new analysis. Every claim traces to a GAL entry.
2. Every claim must be citable in the Evidence Register (Section 8).
3. Hypotheses must never be presented as proven causes.
4. Observations and explanations must be clearly separated throughout the narrative.
5. The report must not require statistical knowledge to read.
6. The report must be honest about uncertainty — overconfident claims are a failure mode.
7. No visualization appears in the report without a plain-language interpretation.

---

## 11. Dependency Map

**Reads from:** All GAL sections (1 through 9)

**Writes to:** GAL Section 10 — Report Memory

**Feeds into:** Nothing. The RG is the final stage of the data science pipeline.

**Is fed by:** ADC (directly — the report narrates the dashboard's selections and recommendations)
