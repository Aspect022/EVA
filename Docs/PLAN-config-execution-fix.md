# /plan - Centralize Configuration and Fix Execution

## 🔴 Phase -1: Context Check
- **Objective:** Centralize all configuration (models, timeouts, API URLs) into a single file and fix execution script reliability.
- **Current State:** 
  - `Backend/config.json` and `Backend/config.py` exist but don't cover everything. 
  - `Frontend/streamlit_app.py` has hardcoded `API_URL = "http://localhost:8000"` and multiple `timeout=800` hardcoded in `requests.post`.
  - Execution is currently manual via two terminals running FastAPI and Streamlit (`STARTUP.md`).
  - Execution errors likely stem from terminal handling, pathing, or uncoordinated startup.

## 🛑 Phase 0: Socratic Gate
Before implementing, I need to clarify a few things regarding the execution failures:
1. **Error Specifics:** When you say "execution is failing most of the times", what exact error messages are you seeing? Is it a Python error on startup, a port-in-use error, or a timeout during analysis?
2. **Environment:** Are you using the provided `.\.venv` virtual environment exactly as described in `STARTUP.md`, or a global Python installation? 
3. **Run script preference:** Would you prefer a single `run.ps1` / `run.bat` file that automatically starts both the backend and frontend in separate windows, or a single Python runner script?

---

## 🔍 Debug: Execution Failing

### 1. Symptom
User reports that running the scripts often fails throwing an error, making the startup process unreliable.

### 2. Information Gathered
- Frontend timeout is hardcoded to 800s in multiple places.
- `STARTUP.md` requires running two manual commands in separate terminals.
- There are no automated cleanup scripts for orphaned processes.

### 3. Hypotheses
1. ❓ **Port Conflicts:** If one of the previous runs didn't shut down properly, ports 8000 (FastAPI) or 8502 (Streamlit) might be quietly blocked, causing the backend to crash on startup.
2. ❓ **Startup Coordination & Pathing:** Running the commands manually might lead to working directory issues if not run from the exact root folder (`d:\Projects\EVA`), causing `ModuleNotFoundError` or file path errors.
3. ❓ **Hardcoded Timeouts/URLs:** Streamlit might be timing out or pointing to a hardcoded URL that doesn't match the actual environment.

### 4. Investigation Plan
- Propose a unified `run.ps1` that cleans up orphaned processes, activates the virtual environment, and correctly starts both servers.
- Aggregate all scattered config variables (like Streamlit timeouts and API endpoints) into a unified `config.json` or `.env` file.

---

## 🛠️ Phase 1-4: Task Breakdown (Pending Approval)

### Task 1: Centralize Configuration
- Abstract Streamlit's `API_URL` and `timeout=800` into `Backend/config.json`.
- Modify `Frontend/streamlit_app.py` to read core settings directly from the unified configuration file.
- Update `Backend/config.py` to ensure all these settings are strongly typed via Pydantic and propagate through all agents.

### Task 2: Unified Execution Script
- Create an intelligent `run.ps1` script in the root directory that:
  - Checks if the `.venv` exists and activates it.
  - Automatically kills previously stuck `uvicorn` and `streamlit` processes on ports 8000 and 8502.
  - Starts the backend in the background.
  - Starts the frontend and opens it in the browser.

### Task 3: Reliability Testing
- Run the `run.ps1` script to verify both servers spin up correctly without port conflicts or path errors.
