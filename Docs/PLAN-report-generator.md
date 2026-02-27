# Plan: Report Generator (RG) Module

## Overview
Implement the **Report Generator (RG)** unit, the final stage of the Data Science pipeline. The RG converts the comprehensive Global Analysis Ledger (GAL) reasoning record (Sections 1-9) into a structured, narrative report tailored to the specific stakeholder (Section 10). 

## Project Type
**BACKEND** (with minor **WEB** frontend view updates)

## Success Criteria
- [ ] `gal_schema.py` is updated to include GAL Section 10 (`ReportMemory`).
- [ ] `RGRules.md` and `RGRules.lite.md` are created to guide LLM report generation.
- [ ] `rg_agent.py` is implemented, pulling data from GAL sections 1-9 to generate the report.
- [ ] LangGraph pipeline incorporates the RG unit.
- [ ] Streamlit UI can trigger and display the final narrative report.

## Tech Stack
- **Python / FastAPI / LangGraph**: Core backend orchestration.
- **Pydantic**: For strict schema validation (GAL Section 10).
- **Streamlit**: For the frontend visualization of the narrative report.

## File Structure
Changes will be isolated to the following paths:
```text
Backend/
  ├── models/gal_schema.py        (modify)
  ├── agents/rg_agent.py          (new)
  ├── rules/RGRules.md            (new)
  ├── rules/RGRules.lite.md       (new)
  └── orchestrator/pipeline.py    (modify)
  └── api/session.py              (modify)
Frontend/
  └── streamlit_app.py            (modify)
```

## Task Breakdown

### 1. Schema Update (GAL Section 10)
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`, `clean-code`
- **Priority**: P0
- **INPUT**: Current `gal_schema.py` and `10_RG_Report_Generator.md`.
- **OUTPUT**: Pydantic models for Report Sections A-H, stakeholder adaptation, and citations. Must be appended to the master GAL schema.
- **VERIFY**: `mypy Backend/models/gal_schema.py` passes without type errors.

### 2. Rules Definition
- **Agent**: `backend-specialist`
- **Skills**: `prompt-engineering`, `plan-writing`
- **Priority**: P1
- **Dependencies**: None
- **INPUT**: `10_RG_Report_Generator.md`.
- **OUTPUT**: `Backend/rules/RGRules.md` and `Backend/rules/RGRules.lite.md` containing prompt instructions emphasizing narrative flow, audience adaptation, and separation of observation from hypothesis. 
- **VERIFY**: Rule files are created and adhere to the project's standard markdown rule structure.

### 3. RG Agent Implementation
- **Agent**: `backend-specialist`
- **Skills**: `api-patterns`, `python-patterns`
- **Priority**: P1
- **Dependencies**: Task 1, Task 2
- **INPUT**: Pydantic schemas and RGRules.
- **OUTPUT**: `Backend/agents/rg_agent.py` containing the `RGAgent` class. It must read GAL sections 1-9, inject them into the LLM context, and parse the output into Section 10.
- **VERIFY**: The agent instantiates without syntax errors and successfully integrates with the existing LLM core execution patterns.

### 4. Pipeline & API Integration
- **Agent**: `backend-specialist`
- **Skills**: `api-patterns`
- **Priority**: P1
- **Dependencies**: Task 3
- **INPUT**: `rg_agent.py`, `pipeline.py`, `session.py`.
- **OUTPUT**: A new API endpoint (e.g., `/session/{session_id}/execute/rg`) and a registered node in the LangGraph `pipeline.py`.
- **VERIFY**: API router spins up cleanly (`uvicorn Backend.main:app`). Manual cURL to the endpoint returns the expected state.

### 5. Frontend UI Integration
- **Agent**: `frontend-specialist`
- **Skills**: `python-patterns`
- **Priority**: P2
- **Dependencies**: Task 4
- **INPUT**: Streamlit capabilities and new backend API endpoint.
- **OUTPUT**: Update `Frontend/streamlit_app.py` to add a "Generate Final Report" button and a dedicated UI component to render the markdown narrative clearly.
- **VERIFY**: `streamlit run Frontend/streamlit_app.py` successfully launches and the UI elements are visible.

## Phase X: Verification
- [ ] Lint: `flake8 Backend/` or equivalent linter passes.
- [ ] Type Check: `mypy Backend/` passes.
- [ ] Schema: Manual verification that `gal_schema.py` can serialize/deserialize Section 10.
- [ ] Build: FastAPI server starts without crash.
- [ ] Run & Test: Run through a dummy dataset, trigger the RG via Streamlit, and verify the report appears in the UI and is saved to `GAL.json`. 
