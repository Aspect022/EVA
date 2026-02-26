# PLAN: IHE Implementation

## Overview
Implementing the Investigation & Hypothesis Engine (IHE), the next core module in the EVA Data Science pipeline (Phase 2). It transforms exploratory findings (Sector 4) into plausible real-world hypotheses (Sector 5) and prepares the state for Human-in-the-Loop (HITL) review.

## Project Type
BACKEND

## Success Criteria
- [ ] `gal_schema.py` updated with Section 5 (Hypotheses).
- [ ] `IHERules.md` created to guide the LLM's causal reasoning efficiently.
- [ ] `ihe_agent.py` implemented to read GAL Sections 1-4 and output valid hypotheses.
- [ ] At least two hypotheses generated per significant observation unless evidence is overwhelming.
- [ ] HITL (Human-in-the-Loop) interrupt mapped out for the orchestration layer.

## Tech Stack
- **Python / Pydantic**: For strict GAL schema parsing and validation.
- **LLM / LangChain**: For invoking the reasoning model with IHE rules.

## File Structure
- `[MODIFY]` `Backend/models/gal_schema.py` - Add Hypothesis schema.
- `[NEW]` `Backend/rules/IHERules.md` - AI reasoning instructions.
- `[NEW]` `Backend/agents/ihe_agent.py` - Core logic for the agent.

## Task Breakdown

### 1. Update GAL Schema
- **Agent**: `backend-specialist`
- **Skills**: `clean-code`, `python-patterns`
- **INPUT**: `06_IHE_Hypothesis_Engine.md` schema definitions.
- **OUTPUT**: Updated `GAL.json` schema inside `gal_schema.py` adding `HypothesisEntry` and `Hypotheses` (Section 5).
- **VERIFY**: `mypy Backend/models/gal_schema.py` passes without type errors.

### 2. Create IHE Reasoning Rules
- **Agent**: `backend-specialist`
- **Skills**: `clean-code`
- **INPUT**: The 7 operational rules and 5-step process from the IHE Design Doc.
- **OUTPUT**: `Backend/rules/IHERules.md` and `Backend/rules/IHERules.lite.md`.
- **VERIFY**: Ensure rule file explicitly forbids claiming causation and mandates multiple explanation generation.

### 3. Implement IHE Agent Logic
- **Agent**: `backend-specialist`
- **Skills**: `python-patterns`, `clean-code`
- **INPUT**: Updated schema and rules.
- **OUTPUT**: `Backend/agents/ihe_agent.py` containing `IHEAgent` class that filters significant findings from EPR, formats context (Sections 1-4), invokes the reasoning LLM, and writes to GAL Section 5.
- **VERIFY**: Manual unit test passing dummy GAL data into IHE and asserting output conforms to Section 5 schema.

### 4. Integration & HITL Pause Stub
- **Agent**: `backend-specialist`
- **Skills**: `architecture`
- **INPUT**: Orchestrator implementation.
- **OUTPUT**: Connect IHE inside the main orchestration pipeline and add the LangGraph breakpoint/interrupt hook for HITL review.
- **VERIFY**: The pipeline stops execution and awaits human input after IHE completes.

## Phase X Verification
- [ ] **Lint**: `python .agent/scripts/checklist.py .` passes
- [ ] **Schema Check**: Pydantic outputs valid JSON matching the new schema
- [ ] **Test**: End-to-end dry run over the `dummy_sales.csv` triggers IHE correctly
