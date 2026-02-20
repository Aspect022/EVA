# EVA — Master Architecture Document
### Autonomous Data Analysis Assistant | Data Science System Specification
**Version 2.0 | Confidential**

---

## 1. What EVA Is

EVA is a personal, self-operating data analyst. A person uploads a dataset and walks away with a clear understanding of what it means, what patterns exist within it, what might be causing those patterns, and what they should do next — without needing to know statistics, programming, or data science.

EVA is not a tool that waits for the user to drive every decision. It is a reasoning system that thinks before it computes, explains everything it does, and grounds every conclusion in traceable evidence.

The promise is simple: upload a dataset, get understanding.

---

## 2. The Core Design Insight

Most automated data systems follow this sequence:

**Upload → Clean → Model → Output**

This is not how a skilled analyst actually works. A real analyst receiving a new dataset does not immediately start cleaning or running algorithms. They spend the first part of their time asking questions about reality: What is this data? What process generated it? What decision does the person need to make? What could go wrong if I misread it?

EVA is built around this insight. Every stage in EVA is downstream of a reasoning step that happens before any computation begins. The system understands first, then acts.

EVA's approach:

**Understand → Question → Repair → Explore → Hypothesize → Engineer → Visualize → Decide → Report**

Each arrow in this chain passes structured, documented reasoning from one stage to the next. No stage is a black box. Every conclusion traces back to a specific piece of evidence. Every action traces back to a specific decision with recorded justification.

---

## 3. The Global Analysis Ledger

The single most important architectural concept in EVA is the **Global Analysis Ledger (GAL)**.

The GAL is the shared reasoning record of an entire analysis session. It is not a log file. It is not a cache. It is the official, permanent, structured record of everything EVA has understood, decided, discovered, and concluded — and why.

Every module in EVA reads from the GAL before acting. Every module writes to the GAL after acting. No module is allowed to work in isolation or make decisions without consulting what came before.

Think of the GAL as the notebook a careful human analyst keeps while working — except it is structured, enforced, and shared across every stage of the analysis.

The GAL is what gives EVA continuity, explainability, and trustworthiness. It is what makes EVA an analyst rather than a pipeline.

A dedicated document describes the GAL in full. The summary here is: if it happened in EVA, it is in the GAL. If it is not in the GAL, it did not happen.

---

## 4. The Pipeline — Canonical Stage Order

EVA's data science pipeline consists of nine stages, executed in the following fixed order. This sequence is the single source of truth. All module documents reference this order.

| Stage | Module | What Happens |
|-------|--------|--------------|
| 0 | Dataset Profiler & Semantic Understanding (DPSU) | EVA reads the raw dataset and builds a real-world understanding of what it represents before touching anything |
| 1 | Question Builder & Intent Inference (QBII) | EVA determines what the user actually wants to learn or decide, and records this as the analytical objective |
| 2 | Data Repair & Integrity Layer (DRIL) | EVA identifies and corrects data quality problems, informed by what the data represents and what the user needs |
| 3 | Exploration & Pattern Recognition (EPR) | EVA discovers what is actually happening in the data — distributions, correlations, anomalies, trends |
| 4 | Investigation & Hypothesis Engine (IHE) | EVA asks why those patterns might exist in the real world and generates structured, testable explanations |
| 5 | Feature Intelligence Engine (FIE) | EVA designs new derived variables that capture real-world meaning not present in the raw columns |
| 6 | Visualization Planner & Executor (VPE) | EVA decides which visual evidence the user needs to see and produces it with clear interpretation |
| 7 | Analytical Dashboard Composer (ADC) | EVA organizes the most important findings into a persistent decision interface |
| 8 | Report Generator (RG) | EVA converts the full reasoning record into a coherent, human-readable narrative document |

**Rule:** No stage may begin until the previous stage has completed and written its output to the Global Analysis Ledger.

**Rule:** No stage may contradict a prior stage's findings without explicitly recording an update in the GAL with justification.

---

## 5. How the Modules Connect

Each module has a defined set of inputs it reads and a defined output it writes. The connections are not arbitrary — they follow the logic of how a real analyst builds understanding over time.

**DPSU** has no module inputs. It reads the raw dataset directly and is the only module that does so. Everything it learns becomes the foundation for all other modules.

**QBII** reads DPSU's output. It cannot ask the right questions without first knowing what kind of dataset it is dealing with.

**DRIL** reads both DPSU and QBII outputs. Cleaning decisions depend on what the data represents and what the user is trying to accomplish. The same missing value might be filled differently depending on both factors.

**EPR** reads DPSU, QBII, and DRIL outputs. Exploration is guided by intent and performed on clean data.

**IHE** reads EPR output and all prior GAL sections. It cannot generate hypotheses without observations to explain, and it needs full context about the domain and user goal to generate relevant ones.

**FIE** reads IHE, DPSU, and QBII outputs. Feature engineering is driven by the hypotheses (what real-world mechanisms might matter), the domain (what variables are meaningful in this context), and the user's objective (what features will actually help).

**VPE** reads EPR, IHE, and FIE outputs. Visualizations are chosen to answer specific questions raised by findings and hypotheses.

**ADC** reads VPE, IHE, and all prior sections. It selects the most decision-relevant elements and organizes them into a coherent interface.

**RG** reads the entire GAL. It does not perform new analysis. It translates everything already recorded into a narrative a non-technical reader can understand and present.

---

## 6. What EVA Is Not

Understanding EVA's boundaries is as important as understanding its capabilities.

EVA is not a modeling system in the current scope. It performs data science — understanding, cleaning, exploration, hypothesis generation, feature design, and visualization. Machine learning model training, evaluation, and deployment are a separate scope handled by a separate pipeline that EVA feeds into.

EVA is not a general-purpose chatbot. It answers questions about the specific dataset it is analyzing, grounded in evidence it has actually found. It does not generate plausible-sounding answers that are disconnected from the data.

EVA is not a reporting shortcut. The Report Generator produces a narrative based on deep, structured reasoning. The report is the final output of a complete reasoning process, not a summary of raw data.

---

## 7. Design Principles That Govern Everything

These principles apply to every module and every decision EVA makes. They are not guidelines — they are rules.

**Intelligence before computation.** EVA understands before it acts. No cleaning, no exploration, no feature engineering happens before the dataset is understood.

**No silent actions.** Every decision EVA makes is recorded in the GAL with justification. If EVA cannot justify a decision, it does not make it.

**Correlation is not explanation.** Observing a pattern is not the same as understanding it. EVA always separates what it found from what it believes might explain it, and always records the uncertainty.

**Intent shapes everything.** The same dataset analyzed for different purposes requires different cleaning decisions, different features, different visualizations, and a different report. User intent is established early and consulted throughout.

**Evidence before recommendation.** EVA never makes a recommendation without citing the specific observations and hypotheses that support it.

**Honesty about uncertainty.** Every output from EVA includes an honest signal about how confident EVA is. Overconfident outputs are a failure mode, not a feature.

**Local first.** User data does not leave the user's environment. All processing happens locally. This is not optional.

---

## 8. The Two Products of EVA

At the end of an analysis session, EVA produces two distinct outputs that serve different purposes.

The **Analytical Dashboard** is a persistent, structured interface that remains available for ongoing use. It shows the most important KPIs, patterns, and alerts in a form that supports continuous decision-making. It is designed to be revisited as the user's understanding deepens or as new data arrives.

The **Analysis Report** is a one-time narrative document that tells the complete story of the analysis — what the data is, what was found, why it might be happening, and what to do. It is designed to be shared with others who were not part of the analysis session.

These are complementary, not redundant. The dashboard keeps the user informed. The report communicates findings to others.

---

## 9. Module Documents

Each module has its own dedicated specification document. The documents are:

- GAL — Global Analysis Ledger
- DPSU — Dataset Profiler & Semantic Understanding
- QBII — Question Builder & Intent Inference
- DRIL — Data Repair & Integrity Layer
- EPR — Exploration & Pattern Recognition
- IHE — Investigation & Hypothesis Engine
- FIE — Feature Intelligence Engine
- VPE — Visualization Planner & Executor
- ADC — Analytical Dashboard Composer
- RG — Report Generator

Each module document covers: purpose, design principle, position in the pipeline, inputs, responsibilities, process, GAL output, failure handling, operational rules, and dependency map.

---

## 10. Definition of Success

EVA succeeds when a completely non-technical person uploads a dataset and says, with genuine understanding:

*"Now I understand my data and I know what to do."*

Every design decision in every module should be evaluated against this standard.
