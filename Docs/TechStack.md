# **EVA Technical Stack Specification**

This is the **actual technology decision document**.

Not optional — this prevents future chaos.

---

## **1\. System Architecture Type**

EVA uses:

Local-first, modular, containerized analytical platform.

Data never leaves user machine .

---

## **2\. Core Technologies**

### **Backend**

Python (primary runtime)

Why:

* ML ecosystem  
* pandas  
* sklearn  
* fast dev

Framework:  
**FastAPI**

Reason:  
async \+ streaming responses \+ LLM compatible

---

### **Frontend**

React \+ TypeScript

Responsibilities:

* upload dataset  
* show findings  
* chat with EVA  
* show model predictions

---

### **LLM Layer**

Local or hybrid:

Options:

* Ollama (local models)  
* API fallback (optional)

LLM is used only for reasoning — not for heavy computation.

---

### **Orchestration**

LangGraph (state machine agents)

Why:  
EVA is not a single chain — it is a reasoning workflow.

---

### **Machine Learning**

Libraries:

* scikit-learn (primary)  
* statsmodels (interpretability)  
* xgboost/lightgbm (optional later)

---

### **Data Processing**

* pandas  
* numpy  
* pyarrow

---

### **Storage**

Not a database.

EVA uses **session-based file storage**:

/eva\_sessions/  
   session\_id/  
      dataset\_snapshot/  
      repaired\_data/  
      learning\_view/  
      models/  
      predictions/  
      GAL.json

Matches reproducibility requirement .

---

### **Model Deployment**

Local container microservice.

Tool:  
Docker

Each trained model becomes:

prediction\_service:5001/predict

---

### **Monitoring**

* Evidently AI (data drift)  
* custom logging

Drift alerts follow defined thresholds .

---

### **Visualization**

* Plotly  
* Vega-Lite

---

## **3\. Why This Stack Works**

Because EVA is:

NOT SaaS analytics  
NOT a notebook  
NOT a chatbot

It is:

a reasoning system \+ analytical engine \+ decision assistant

So the stack must support:

* state  
* reproducibility  
* traceability  
* local privacy  
* iterative reasoning

---

# **What You Now Have**

You now have:

• Vision PRD (already)  
• ML Master PRD (already)  
• **System Execution PRD (NEW — missing bridge)**  
• **Tech Stack Specification (NEW — engineering foundation)**

Together, this becomes a **real buildable software architecture**.

