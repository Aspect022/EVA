<div align="center">
  
# 🧠 EVA: Autonomous Data Science OS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)

*An autonomous data science assistant and reasoning operating system.*
<br>
**EVA is not just a chatbot; it is a session-based analytical OS designed to perform Understanding, Reasoning, Hypothesis Generation, Evidence Gathering, and Learning.**

Every action EVA takes is logged in an append-only **Global Analysis Ledger (GAL)** to ensure transparency, reproducibility, and human oversight.

---
</div>

## ✨ Key Features

| Module | Description |
|--------|-------------|
| 📜 **Global Analysis Ledger (GAL)** | A pure JSON-based append-only ledger tracking every reasoning step, hypothesis, and data transformation. |
| 📊 **Dataset Profiler (DPSU)** | Autonomously infers row meaning, column roles, and domain context from raw CSV uploads. |
| 🎯 **Intent Inference (QBII)** | Understands analytical goals and stakeholder context. |
| 🛠️ **Data Repair (DRIL)** | Fixes missing values, duplicates, and outliers with explicit reasoning written to the GAL. |
| 💡 **Hypothesis Engine (IHE)** | Generates plausible real-world hypotheses per observation, with a strict Human-In-The-Loop (HITL) pause for user validation. |
| 🤖 **Machine Learning Layer (MLRL)**| Containerized, evidence-bound ML execution triggered only after hypothesis authorization. |

---

## 🚀 Quick Start Guide

<details open>
<summary><b>1️⃣ Prerequisites</b></summary>
<br>

Ensure Ollama is running with the `gpt-oss:120b-cloud` model pulled:
```powershell
ollama pull gpt-oss:120b-cloud
```

Activate your Python Virtual Environment:
```powershell
.\.venv\Scripts\Activate.ps1
```
</details>

<details open>
<summary><b>2️⃣ Running the System</b></summary>
<br>

You will need two terminal windows running simultaneously to start both the backend API and frontend UI.

**⚡ Terminal A: Backend (FastAPI)**
```powershell
.\.venv\Scripts\python.exe -m uvicorn Backend.api.main:app --reload
```
> 📍 **API URL**: `http://localhost:8000`  
> 📖 **API Docs**: `http://localhost:8000/docs`

**🖥️ Terminal B: Frontend (Streamlit / React)**
```powershell
.\.venv\Scripts\python.exe -m streamlit run Frontend\streamlit_app.py
```
> 🌐 **UI URL**: `http://localhost:8502`
</details>

---

## 📂 Project Structure

```text
EVA/
├── ⚙️ Backend/          # FastAPI app, LangGraph orchestrator, reasoning agents, GAL storage
├── 🎨 Frontend/         # User interfaces (Streamlit app & React OS dashboard)
├── 🧠 Agents/           # Specialized reasoning modules and ML utilities
├── 📚 Docs/             # Architecture documentation, design records
└── 📁 eva_sessions/     # UUID-based session state directories (GAL & data snapshots)
```

> **Tip:** Click on the module names below to view their specific READMEs:
> [`/Backend`](./Backend/README.md) • [`/Frontend`](./Frontend/README.md) • [`/Agents`](./Agents/README.md) • [`/Docs`](./Docs/README.md)

---

## ⚙️ Configuration

The system uses local environment variables and JSON configurations located in the `Backend` directory.

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| `PORT` | Backend API port | `8000` |
| `OLLAMA_URL` | Local Ollama endpoint | `http://localhost:11434` |

---

## 📖 Documentation & Planning

Explore the deep architecture and implementation progress of EVA:

- 🏛️ [Master Architecture](./Docs/EVA-DataScience/Mini-Docs/01_EVA_Master_Architecture.md)
- 📈 [Implementation Tracker](./Implementation_Tracker.md)
- 🛣️ [Phased Plan](./eva-phased-plan.md)

---

<div align="center">
  <i>Developed with ❤️ for Autonomous Data Science</i>
</div>
