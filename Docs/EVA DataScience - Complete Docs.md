# **EVA System Execution PRD**

*(The Real One — How the system actually runs)*

This document becomes the **index of the whole project**.  
Every other document plugs into it.

You already have the conceptual PRD (vision \+ behavior) .  
You already have the ML reasoning layer master .

But those answer **what EVA is**.

This new PRD answers:

How EVA operates internally as a running software system.

---

## **1\. Purpose of This PRD**

This document defines:

• system runtime behavior  
• agent orchestration  
• data flow  
• when each module activates  
• how baseline vs detailed reasoning is chosen  
• how code is structured  
• what happens during a session lifecycle

This is the **engineer’s map of EVA**.

---

## **2\. Core Principle (VERY IMPORTANT)**

EVA is **NOT a chatbot with tools**.

EVA is:

A session-based analytical operating system.

Every dataset creates a **temporary analytical universe**.

Inside that universe:

* agents reason  
* modules execute  
* ledger records memory  
* models may or may not be built

The ML layer activates only after reasoning determines prediction is necessary .

---

## **3\. The Single Most Important Concept**

### **EVA Has Two Thinking Modes**

This is what you asked:

baseline information vs detailed analysis

We formalize it.

### **Mode 1 — Rapid Analytical Mode (Baseline)**

Fast, conversational, low compute.

Used for:  
• quick questions  
• column explanations  
• summaries  
• “what does this dataset look like?”

No modeling.  
No heavy pipeline.

Only:

* dataset profiler  
* exploration agent  
* explanation generator

---

### **Mode 2 — Deep Investigation Mode (Full Pipeline)**

Triggered when:

* prediction  
* risk scoring  
* classification  
* forecasting

This activates the ML reasoning pipeline .

This is the **real EVA**.

---

## **4\. Session Lifecycle (THIS IS THE IMPLEMENTATION HEART)**

Every upload creates:

Analysis Session  
session\_id \= UUID

The system immediately creates a GAL (shared reasoning memory) .

---

### **Step-By-Step Runtime**

### **STEP 0 — Session Creation**

Backend:

POST /session/create

Server:

* generates session\_id  
* creates directory  
* initializes empty GAL.json

---

### **STEP 1 — Dataset Cognition Agent**

Input: raw CSV

Runs:

* column typing  
* row meaning inference  
* time behavior  
* target candidates

Writes → GAL.dataset\_identity

(No cleaning yet — understanding first, matching real analyst workflow )

---

### **STEP 2 — Cleaning Agent**

Reads: dataset\_identity

Performs:

* missing value handling  
* duplicates  
* type correction

Writes → GAL.data\_integrity\_record

---

### **STEP 3 — Exploration Agent**

Creates:

* distributions  
* correlations  
* anomalies

Writes → GAL.exploratory\_findings

---

### **STEP 4 — Hypothesis Agent (CRITICAL)**

Converts patterns → possible real-world explanations .

Writes → GAL.hypotheses

This stage is what separates EVA from AutoML.

---

### **DECISION GATE (VERY IMPORTANT)**

Chairman Agent evaluates:

Does the user require prediction?

If NO →  
EVA stops here → generates report.

If YES →  
Machine Learning Reasoning Layer activates .

---

## **5\. ML Pipeline Activation**

Once activated:

### **PFTDC**

Defines problem & builds Learning View (training dataset) .

### **MCG**

Chooses 2–4 candidate model families .

### **TEM**

Trains and evaluates candidates .

### **RVEM**

Checks explanation validity & leakage .

### **PMDD**

Deploys & monitors model .

All communication happens through the Global Analysis Ledger (no direct module communication) .

---

## **6\. How the Agents Are Designed (Code Architecture)**

Agents are NOT separate AIs.

They are:

Prompt-programmed controllers wrapped around tools.

Each agent:

Agent \=  
(LLM reasoning brain)  
\+  
(toolbox)  
\+  
(GAL reader/writer)

Example:

### **Cleaner Agent**

Tools:

* pandas operations  
* schema validator  
* anomaly detector

### **Feature Engineer**

Tools:

* feature generation library  
* domain rules

### **Model Architect**

Tools:

* sklearn  
* training executor  
* evaluation engine

The LLM decides **what to do**.  
Python tools do **the action**.

---

## **7\. How Code Is Actually Structured**

We divide the backend into 4 layers.

### **Layer 1 — API Layer**

Handles user interaction.

Endpoints:

/upload  
/ask  
/predict  
/report

---

### **Layer 2 — Orchestrator**

The real brain.

Responsibilities:

* which agent runs next  
* read/write GAL  
* mode switching  
* error recovery

Think:

LangGraph / state machine controller.

---

### **Layer 3 — Agents**

Each agent:

* reads GAL  
* reasons  
* calls tools  
* writes results

---

### **Layer 4 — Compute Tools**

Pure Python.

Includes:

* pandas  
* sklearn  
* statsmodels  
* monitoring

Agents never directly edit dataset files.  
They issue commands to tools.

---

## **8\. Failure Behavior (Critical Engineering Detail)**

If a stage fails:

| Failure | System Behavior |
| ----- | ----- |
| modeling invalid | fallback to descriptive analysis |
| all models rejected | re-frame problem |
| drift detected | request new analysis |

Pipeline halt behavior is mandatory .

---

## **9\. Phased Development Plan (What you asked)**

We split implementation into clear phases.

### **Phase 1 — Dataset Intelligence**

Profiler, cleaning, exploration, report generation.

*(You can demo EVA here.)*

### **Phase 2 — Hypothesis & Feature Reasoning**

Now EVA becomes different from AutoML.

### **Phase 3 — ML Reasoning Layer**

Full 5-module pipeline.

### **Phase 4 — Prediction Service**

Model deployment & monitoring.

### **Phase 5 — Conversational Analyst**

Question answering over session memory.

### **Phase 6 — Continuous Monitoring**

Future expansion.

# 

