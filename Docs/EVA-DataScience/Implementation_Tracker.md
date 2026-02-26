# EVA Data Science: Implementation Tracker

This document provides a phase-wise roadmap for the EVA Data Science pipeline, tracking what has been implemented and what is upcoming. Team members can use this to identify their next tasks and follow the corresponding architectural designs.

---

## Phase 1: Core System & Data Foundation (✅ Implemented)
This phase establishes the foundational architecture, data understanding, user intent, data repair, and basic pattern recognition.

### 1. Master Architecture & GAL (✅ Implemented)
* **Design Docs:** 
  * [01_EVA_Master_Architecture.md](./Mini-Docs/01_EVA_Master_Architecture.md)
  * [02_GAL_Global_Analysis_Ledger.md](./Mini-Docs/02_GAL_Global_Analysis_Ledger.md)
* **Status:** `gal_schema.py` is implemented and currently models GAL Sections 1 through 4. It acts as the unalterable source of truth.

### 2. DPSU - Dataset Profiler & Semantic Understanding (✅ Implemented)
* **Design Doc:** [03_DPSU_Dataset_Profiler.md](./Mini-Docs/03_DPSU_Dataset_Profiler.md)
* **Status:** `dpsu_agent.py` is implemented. It successfully infers row meaning, column roles, and real-world domain purely from raw data.

### 3. QBII - Question Builder & Intent Inference (✅ Implemented)
* **Design Doc:** [04_QBII_Question_Builder.md](./Mini-Docs/04_QBII_Question_Builder.md)
* **Status:** `qbii_agent.py` is implemented. It handles user constraints, analytical goals, and stakeholder types to guide downstream behavior.

### 4. DRIL - Data Repair & Integrity Layer (✅ Implemented)
* **Design Doc:** [05_DRIL_Data_Repair.md](./Mini-Docs/05_DRIL_Data_Repair.md)
* **Status:** `dril_agent.py` is implemented. Corrects data issues (missing values, duplicates, outliers) while explicitly writing justifications to the GAL.

### 5. EPR - Exploration & Pattern Recognition (✅ Implemented)
* **Design Doc:** [06a_EPR_Exploration_Pattern_Recognition.md](./Mini-Docs/06a_EPR_Exploration_Pattern_Recognition.md)
* **Status:** `epr_agent.py` is implemented. Observes distributions, correlations, and anomalies without generating premature hypotheses.

---

## Phase 2: Advanced Reasoning & Feature Engineering (🚀 Next Up)
This phase transitions the system from merely *describing* data to *explaining* patterns and preparing the dataset for modeling. **This is currently the active development phase.**

### 6. IHE - Investigation & Hypothesis Engine (📝 To Be Implemented)
* **Design Doc:** [06_IHE_Hypothesis_Engine.md](./Mini-Docs/06_IHE_Hypothesis_Engine.md)
* **Implementation Goal:** Build `ihe_agent.py`. This module must read the findings from EPR and generate plausible real-world hypotheses (with competing theories and plausibility scores).
* **Dependencies:** Requires an update to `gal_schema.py` to support Section 5 (Hypotheses).

### 7. FIE - Feature Intelligence Engine (📝 To Be Implemented)
* **Design Doc:** [07_FIE_Feature_Intelligence.md](./Mini-Docs/07_FIE_Feature_Intelligence.md)
* **Implementation Goal:** Build `fie_agent.py` as a sophisticated **Multi-Domain RAG system**. It needs to pull domain-specific knowledge bases to construct a `Feature Plan JSON` showing exactly what features to engineer and why.

---

## Phase 3: Communication & Visualization (⏳ Planned)
This phase focuses on rendering the reasoning into understandable visuals, persistent dashboards, and sharable reports for the end user.

### 8. VPE - Visualization Planner & Executor (⏳ Planned)
* **Design Doc:** [08_VPE_Visualization_Planner.md](./Mini-Docs/08_VPE_Visualization_Planner.md)
* **Implementation Goal:** Build `vpe_agent.py` with separate *Planner* (deciding *why* and *what* to visualize) and *Executor* (the actual rendering of the chart) components.

### 9. ADC - Analytical Dashboard Composer (⏳ Planned)
* **Design Doc:** [09_ADC_Dashboard_Composer.md](./Mini-Docs/09_ADC_Dashboard_Composer.md)
* **Implementation Goal:** Build `adc_agent.py`. This module curates KPIs, alerts, and guided recommendations into a structured UI definition (creating an ongoing decision workspace).

### 10. RG - Report Generator (⏳ Planned)
* **Design Doc:** [10_RG_Report_Generator.md](./Mini-Docs/10_RG_Report_Generator.md)
* **Implementation Goal:** Build `rg_agent.py`. The final step that compiles the entire GAL reasoning record into a cohesive, human-readable narrative report explaining the dataset, findings, and recommendations.
