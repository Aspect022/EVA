# Backend - EVA Data Science OS

This directory contains the core reasoning, orchestration, and storage backend for EVA. It is built using Python, FastAPI, LangGraph, and various data-science focused utilities.

## Quick Start

### 1. Requirements

Ensure you have your Python virtual environment activated:
```powershell
.\..\.venv\Scripts\Activate.ps1
```

Install dependencies if needed:
```powershell
pip install -r requirements.txt
```

### 2. Running the API

Start the FastAPI application:
```powershell
python -m uvicorn api.main:app --reload
```
The API is available at `http://localhost:8000`. Documentation available at `http://localhost:8000/docs`.

## Directory Structure

| Directory | Description |
|-----------|-------------|
| `api/` | FastAPI routes, controllers, and dependency injection. |
| `agents/` | Individual reasoning modules (e.g., DPSU, QBII, DRIL, IHE). |
| `orchestrator/` | LangGraph state machines controlling the flow between agents. |
| `models/` | Pydantic data schemas representing the Global Analysis Ledger (GAL). |
| `storage/` | Utilities for saving dataset snapshots to disk and keeping the `GAL.json` append-only logs safe. |
| `mlrl/` | Machine Learning Reasoning Layer for model generation and execution. |
| `rag/` | Retrieval Augmented Generation utilities. |
| `rules/` | Prompt rules and definitions dictating agent behaviors. |
| `tools/` | Reusable utilities and helper scripts for the backend. |

## Configuration

Configuration is managed via `config.json` and `config.py`.

| Variable | Description |
|----------|-------------|
| `PORT` | API Port (Default: 8000) |
| `BASE_DATA_DIR` | Location to save `eva_sessions` |

## Documentation

For architectural specifics, see:
- [01_EVA_Master_Architecture.md](../Docs/EVA-DataScience/Mini-Docs/01_EVA_Master_Architecture.md)
- [02_GAL_Global_Analysis_Ledger.md](../Docs/EVA-DataScience/Mini-Docs/02_GAL_Global_Analysis_Ledger.md)
- [06_IHE_Hypothesis_Engine.md](../Docs/EVA-DataScience/Mini-Docs/06_IHE_Hypothesis_Engine.md)

## License
MIT
