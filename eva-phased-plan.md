# EVA - Phased Implementation Plan v2.0

## Overview
EVA is an autonomous data science assistant designed as a reasoning OS, not a generic chatbot. The core principle is **Understanding → Reasoning → Hypothesis → Evidence → Learning**. Every action is logged in an append-only **Global Analysis Ledger (GAL)**. The system is split into two massive sub-systems: the **Data Science Pipeline (9 stages)** and the **Machine Learning Reasoning Layer (MLRL - 5 modules)**.

## Key Architectonic Constraints & User Answers
- **Storage Mechanism**: Adopting pure JSON (`GAL.json`) stored on-disk per session. No SQLite for now. Folders will hold data snapshots, learning views, and model artifacts explicitly.
- **Orchestration & HITL**: LangGraph will orchestrate the pipeline, but there will be a **Human-In-The-Loop (HITL)** pause built-in specifically at the Hypothesis Engine (IHE) and Critic/Decision Gate. The user will have a live view of the execution state and can intervene/validate hypotheses before ML continues.
- **Data Ingestion**: Standardized to flat file uploads initially (100% CSV focused), ensuring Phase 1 can rely entirely on pandas dataframes before complex schema handling is required.
- **Microservices vs Monolith**: The MLRL modules (PFTDC, MCG, TEM, RVEM, PMDD) must be designed to run as independent containerized services that communicate *strictly* by reading/writing to the GAL.

## Technical Foundation
- **Session State**: UUID-based directories: `/eva_sessions/<uuid>/`
  - Artifacts: `dataset_snapshot/`, `repaired_dataset/`, `feature_view/`, `learning_view/`, `model_candidates/`, `evaluation_results/`, `selected_model/`, `prediction_logs/`, `GAL.json`
- **Core Orchestrator**: LangGraph state machine tracking pipeline progression and waiting on HITL interrupts.
- **Core Technology**: Python, FastAPI, Pandas, scikit-learn, Docker.
- **Frontend**: Streamlit (Temporary Phase 1 testing UI) → React + TypeScript (Phase 4 final UI).

---

## Task Breakdown & Phased Roadmap

### Phase 1: Core Foundation & Dataset Intelligence
*Goal: Build the session storage handler, the GAL manager, and the first four analytical agents.*
1. **API & Storage Foundation**
   - **Agent**: `backend-specialist` + `python-patterns`
   - **Task**: Create standard FastAPI endpoints for `/upload` (CSV) and `/session/create`. Initialize the `GAL.json` schema and file structure.
2. **DPSU (Dataset Profiler) & QBII (Question Builder)**
   - **Agent**: `backend-specialist` + `clean-code`
   - **Task**: Build the agents that infer row meaning, domain, target candidates (Section 1 of GAL) and user intent/objective (Section 2 of GAL).
3. **DRIL (Data Repair) & EPR (Exploration & Pattern Recognition)**
   - **Agent**: `backend-specialist`
   - **Task**: Implement autonomous missing-value handling, type correction, and pattern/correlation detection using standard pandas utilities triggered by LLM reasoning.
4. **Temporary Streamlit Testing UI**
   - **Agent**: `frontend-specialist` + `python-patterns`
   - **Task**: Build a rapid Streamlit application to handle CSV uploads, execute the Phase 1 backend endpoints (`/session/create` and `/upload`), and display the initial Dataset Identity and Exploratory Findings. This will serve as the testing interface until the React frontend is built.

### Phase 2: Hypothesis Reasoning & Human-in-the-Loop
*Goal: Implement the core differentiator of EVA: Causal Reasoning with Human Oversight.*
1. **IHE (Investigation & Hypothesis Engine) & HITL Integration**
   - **Agent**: `backend-specialist` + `orchestrator`
   - **Task**: Generate real-world explanations for found patterns (GAL Section 5). 
   - **Crucial**: Implement LangGraph interrupt / HITL webhook so the UI can prompt the user to validate, reject, or question hypotheses before proceeding.
2. **FIE (Feature Intelligence Engine)**
   - **Agent**: `backend-specialist`
   - **Task**: Post-HITL approval, build domain-aware derived columns based on hypotheses and write the `feature_view` frame.

### Phase 3: Machine Learning Reasoning Layer (MLRL)
*Goal: Containerized, evidence-bound machine learning triggered ONLY if authorized.*
1. **Decision Gate & PFTDC (Problem Framing & Training Data Construction)**
   - **Agent**: `backend-specialist`
   - **Task**: Gate evaluation. If prediction is greenlit, formulate the learning problem, deal with class imbalances, handle time splits, and write the `learning_view` subset.
2. **MCG (Model Candidate Generator) & TEM (Training & Evaluation)**
   - **Agent**: `backend-specialist` + `docker-expert`
   - **Task**: Reason over available algorithms (prioritizing interpretability) and train multiple models cleanly without target leakage.
3. **RVEM (Reliability Validation) & PMDD (Prediction Deployment)**
   - **Agent**: `devops-engineer` + `backend-specialist`
   - **Task**: Validate hypotheses against the trained model. If valid, containerize the model as an isolated microservice (via Docker) with continuous data/confidence drift monitoring hooks.

### Phase 4: Display & Live Interaction
*Goal: The front-end view where users upload, watch EVA think, review hypotheses, and view the final report.*
1. **Live Reasoning UI & HITL Prompts**
   - **Agent**: `frontend-specialist` + `ui-ux-pro-max`
   - **Task**: Build a React dashboard consuming Server-Sent Events (SSE) or WebSockets from the LangGraph orchestrator to show live GAL updates and handle the HITL approval step.
2. **ADC (Analytical Dashboard) & RG (Report Generator)**
   - **Agent**: `frontend-specialist` + `backend-specialist`
   - **Task**: Finalize the analysis with a narrative summary and structured decision-support widgets based strictly on GAL citations.

---

## Verification Plan
1. **Automated Verification**:
   - Run `pytest` on the GAL Append-Only handlers to ensure previous states cannot be overwritten silently without contradiction logs.
   - Run unit tests to mock LangGraph's HITL pause to ensure pipeline state resumes perfectly from disk.
   - Run standard code linting and type-checks (`npx tsc --noEmit` on React, `mypy` on Python).
2. **Manual End-to-End Verification**:
   - Upload the classic Titanic `csv` dataset or a Dummy Sales `csv` through the UI.
   - Watch the Live Reasoning view populate Sections 1 through 4 of the GAL.
   - Trigger the Human-In-The-Loop prompt at the Hypothesis stage.
   - Validate and Authorize ML execution.
   - Verify `prediction_service:5001` container spins up cleanly for the finalized model.
