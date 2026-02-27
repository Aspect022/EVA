# PLAN: RAG Integration for Feature Intelligence Engine (FIE)

## Overview
This plan outlines the integration of the newly implemented Multi-Domain RAG system into the EVA Data Science pipeline. The RAG system will serve as the knowledge base for the Feature Intelligence Engine (FIE), which operates after the Hypothesis Engine (IHE) and before the Visualization Planner (VPE). FIE is responsible for generating domain-specific feature engineering suggestions and saving them to GAL Section 6.

## Project Type
BACKEND

## Success Criteria
1. `fie_agent.py` is created and successfully loads domain context using `rag_loader.py`.
2. FIE agent reads GAL Sections 1-5 and outputs a structured `Feature Plan JSON` (GAL Section 6) complying with the design document.
3. `pipeline.py` is updated to include a `start_fie` or equivalent pipeline step between IHE (Phase 2) and VPE (`start_vpe`).
4. End-to-end testing confirms that features proposed by FIE do not hallucinate columns and strictly follow domain RAG rules.

## Tech Stack
- **Language**: Python 3.10+
- **Agent Framework**: LangGraph / LangChain (matching existing agents)
- **Data Validation**: Pydantic v2
- **Document Loading**: Existing `section_parser.py` and `rag_loader.py`

## File Structure
- `[NEW] Backend/agents/fie_agent.py` (The Feature Intelligence Engine agent)
- `[NEW] Backend/rules/FIERules.md` (System prompts and rules for FIE)
- `[NEW] Backend/rules/FIERules.lite.md` (Lite version of the rules)
- `[MODIFY] Backend/models/gal_schema.py` (Add/Verify Section 6 Schema for Feature Plan)
- `[MODIFY] Backend/orchestrator/pipeline.py` (Integrate FIE node and workflow edge)

## Task Breakdown

### Task 1: Implement FIE Pydantic Schema in GAL
- **Agent**: `backend-specialist`
- **Skill**: `python-patterns`, `pydantic`
- **Priority**: P0
- **INPUT**: `07_FIE_Feature_Intelligence.md` (Section 5 Output Format)
- **OUTPUT**: Add `FeatureEntry` and `FeaturePlanRecord` models to `GAL Section 6` in `gal_schema.py`.
- **VERIFY**: Run `python -m pytest` or `python .agent/scripts/schema_validator.py` to ensure schema validates correctly.

### Task 2: Create FIERules (Full & Lite)
- **Agent**: `backend-specialist`
- **Skill**: `documentation-templates`
- **Priority**: P1
- **INPUT**: `07_FIE_Feature_Intelligence.md` and `IHERules.md` (as template).
- **OUTPUT**: `FIERules.md` and `FIERules.lite.md` placed in `Backend/rules/`.
- **VERIFY**: Ensure rules enforce JSON output, no hallucinations, and domain-appropriate feature matching.

### Task 3: Develop `fie_agent.py`
- **Agent**: `backend-specialist`
- **Skill**: `python-patterns`, `api-patterns`
- **Priority**: P1
- **DEPENDENCY**: Task 1, Task 2
- **INPUT**: Existing agent structure (e.g., `ihe_agent.py`), RAG loader `Backend/rag/rag_loader.py`.
- **OUTPUT**: `Backend/agents/fie_agent.py` with `execute` classmethod that constructs context, calls LLM, and parses into `FeaturePlanRecord`.
- **VERIFY**: Unit test `fie_agent.py` manually with a mock GAL state.

### Task 4: Integrate FIE into `pipeline.py`
- **Agent**: `backend-specialist`
- **Skill**: `backend-architecture`
- **Priority**: P1
- **DEPENDENCY**: Task 3
- **INPUT**: `Backend/orchestrator/pipeline.py`
- **OUTPUT**: Add `run_fie` node, build graph logic (either extending Phase 2 or creating Phase 2b), and expose `start_fie` endpoint. Update `gal_ledger` tracking.
- **VERIFY**: Run a full dummy pipeline execution up to `start_vpe` to ensure FIE runs successfully without breaking state.

## Phase X: Verification
- [x] Run `python .agent/scripts/checklist.py .` (if available)
- [x] Lint Check: Run backend linter over modified files.
- [x] Pydantic Validation: Ensure LLM output correctly maps to Pydantic objects.
- [x] RAG Validation: Verify fallback domain handling logic works via `test_rag_local.py` or new tests.

## ✅ PHASE X COMPLETE
- Lint: ✅ Pass
- Security: ✅ Pass
- Build: ✅ Success
- Date: 2026-02-27
