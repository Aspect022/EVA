# Frontend - EVA Data Science OS

This directory contains the user interface implementations for the EVA Data Science OS.

## Overview
The frontend is split into two distinct implementations based on the project phase:

1. **Streamlit (Phase 1 Testing UI)**: A rapid prototyping interface designed to test the Backend API, file upload, and initial GAL (Global Analysis Ledger) trace. 
2. **React_Based (Phase 4 Final UI)**: The production-ready, cinematic, dark-themed OS dashboard built with Next.js and Tailwind CSS.

## Quick Start (Streamlit Testing)

To run the Streamlit application for testing Phase 1 backend capabilities:

```powershell
.\..\.venv\Scripts\Activate.ps1
python -m streamlit run streamlit_app.py
```
The Streamlit interface will be available at `http://localhost:8502`.

For the production React interface, please see [`React_Based/README.md`](./React_Based/README.md).

## Directory Structure

| Directory/File | Description |
|----------------|-------------|
| `streamlit_app.py` | Main entry point for the Streamlit testing UI. |
| `pages/` | Additional Streamlit pages for multipage routing (e.g., visualizers). |
| `React_Based/` | The Next.js production user interface. |

## Documentation
- [EVA Master Prompt](../EVA_Master_Website_Prompt.md)
- [React Migration Plan](../PLAN-react-migration.md)

## License
MIT
