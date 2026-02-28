# EVA: Autonomous Data Science OS

An autonomous data science assistant and reasoning operating system. EVA is not just a chatbot; it is a session-based analytical OS designed to perform Understanding, Reasoning, Hypothesis Generation, Evidence Gathering, and Learning. 

Every action EVA takes is logged in an append-only **Global Analysis Ledger (GAL)** to ensure transparency, reproducibility, and human oversight.

## Quick Start

### 1. Prerequisites
- **Ollama**: Ensure Ollama is running with the `gpt-oss:120b-cloud` model pulled.
  ```powershell
  ollama pull gpt-oss:120b-cloud
  ```
- **Python Virtual Environment**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

### 2. Running the System
You need two terminal windows running simultaneously:

**Terminal A: Backend (FastAPI)**
```powershell
.\.venv\Scripts\python.exe -m uvicorn Backend.api.main:app --reload
```
- API URL: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

**Terminal B: Frontend (Streamlit / React)**
```powershell
.\.venv\Scripts\python.exe -m streamlit run Frontend\streamlit_app.py
```
- UI URL: `http://localhost:8502`

## Features

- **Global Analysis Ledger (GAL)**: A pure JSON-based append-only ledger tracking every reasoning step, hypothesis, and data transformation.
- **Dataset Profiler (DPSU)**: Autonomously infers row meaning, column roles, and domain context from raw CSV uploads.
- **Intent Inference (QBII)**: Understands analytical goals and stakeholder context.
- **Data Repair (DRIL)**: Fixes missing values, duplicates, and outliers with explicit reasoning written to the GAL.
- **Hypothesis Engine (IHE)**: Generates plausible real-world hypotheses per observation, with a strict Human-In-The-Loop (HITL) pause for user validation.
- **Machine Learning Reasoning Layer (MLRL)**: Containerized, evidence-bound ML execution triggered only after hypothesis authorization.

## Project Structure

- [`/Backend`](./Backend/README.md): FastAPI application, LangGraph orchestrator, reasoning agents, and GAL storage.
- [`/Frontend`](./Frontend/README.md): User interfaces, including a temporary Streamlit app and the main React-based OS dashboard.
- [`/Agents`](./Agents/README.md): Specialized reasoning modules and ML utilities.
- [`/Docs`](./Docs/README.md): Architecture documentation, design records, and tracking.
- [`/eva_sessions`](./eva_sessions): UUID-based session state directories containing the GAL and dataset snapshots.

## Configuration

The system uses local environment variables and JSON configurations located in the `Backend` directory.

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Backend API port | 8000 |
| OLLAMA_URL | Local Ollama endpoint | http://localhost:11434 |

## Documentation

- [Master Architecture](./Docs/EVA-DataScience/Mini-Docs/01_EVA_Master_Architecture.md)
- [Implementation Tracker](./Implementation_Tracker.md)
- [Phased Plan](./eva-phased-plan.md)

## License
MIT
