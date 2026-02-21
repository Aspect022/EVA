# 🚀 EVA Startup Guide

Follow these steps to get the system running locally on your Windows machine.

## 1. Prerequisites
- **Ollama**: Ensure Ollama is running on your system with the `gpt-oss:120b-cloud` model pulled.
  ```powershell
  ollama pull gpt-oss:120b-cloud
  ```

## 2. Virtual Environment
The project uses a dedicated virtual environment in the `.venv` folder. Always use this to avoid dependency conflicts.

**To activate (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 3. Running the System

You need **two terminal windows** (or tabs) running simultaneously:

### Terminal A: Backend (FastAPI)
This handles the reasoning agents, GAL storage, and the LangGraph pipeline.
```powershell
.\.venv\Scripts\python.exe -m uvicorn Backend.api.main:app --reload
```
- **URL**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs`

### Terminal B: Frontend (Streamlit)
This is the temporary testing UI for Phase 1.
```powershell
.\.venv\Scripts\python.exe -m streamlit run Frontend\streamlit_app.py
```
- **URL**: `http://localhost:8502`

---

## 4. First Run Testing
1. Open the Streamlit URL.
2. Click **"Initialize New Session"**.
3. Upload the `dummy_sales.csv` provided in the root directory.
4. Click **"Execute Intelligence Phase 1"**.
5. Watch the **GAL** populate on the right-hand panel with local intelligence!
