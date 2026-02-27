# ADC Implementation

## Goal
Implement the ADC (Analytical Dashboard Composer) agent to generate decision-focused KPIs, dashboard layouts, and action guidance based on GAL reasoning, preparing the data for the frontend.

## Tasks
- [ ] Task 1: Update GAL Schema -> Verify: `python -c "from Backend.models.gal_schema import GlobalAnalysisLedger"` runs error-free.
- [ ] Task 2: Create `ADCRules.md` and `ADCRules.lite.md` -> Verify: Files exist and follow the EVA system prompt format, incorporating Domain Dictionary and Hybrid Action constraints.
- [ ] Task 3: Build `adc_agent.py` -> Verify: Import `ADCAgent` without syntax errors and verify prompt logic matches Pydantic output.
- [ ] Task 4: Integrate in `pipeline.py` -> Verify: `start_adc` (or Phase 3 workflow) runs and correctly serializes `gal.dashboard_plan` to disk.
- [ ] Task 5: Add API Route -> Verify: Add endpoint to `Backend/api/routes/session.py` and start `uvicorn Backend.main:app` successfully.
- [ ] Task 6: End-to-End Execution -> Verify: Run a test session via a dummy script, confirming `GAL.json` contains a perfectly formatted Section 9 Dashboard Plan.

## Done When
- [ ] Schema is robust and properly handles Pydantic edge cases.
- [ ] `ADCAgent` executes over a populated GAL, avoiding hallucinations through strict prompt bounds.
- [ ] Frontend has access to pure JSON data for Panel A, B, C, and D layout via the API.
- [ ] The `{task-slug}.md` file is marked complete.

## Notes
- As agreed, ADC UI Rendering is handled by frontend (React) using "Pure GAL Data."
- KPI Synthesis relies on Domain Dictionary / RAG to avoid metrics that cannot be calculated.
- Action Guidance leverages a Hybrid approach, tightly constrained by hypothesis plausibility.
