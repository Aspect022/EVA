# EVA - Frontend UI/UX Architecture & Component Specification

This document defines the exact pages, views, and components required to build the Next.js frontend for EVA. It translates the EVA Data Science and ML pipelines into a concrete, interactive user interface.

## 1. Core Concept: The Analytical Universe
EVA is an autonomous data science assistant. When a user uploads a dataset, it creates a "temporary analytical universe" (a Session). The UI is a glass window into EVA's brain, allowing the user to watch agents reason, clean, explore, and model data, with a critical Human-In-The-Loop (HITL) pause before machine learning is executed.

**Design System:**
- OLED Dark Mode (Deep Blacks `#000000`, `#09090b`)
- Primary: Blue `#3B82F6` | Secondary/CTA: Orange `#F97316`
- **STRICT RULE:** No Purple/Violet hex codes.
- Typography: Fira Code or similar technical sans-serif.

---

## 2. Pages Required (App Router Structure)

### `app/page.tsx` - The Landing & Session Manager
**Purpose:** The entry point. A clean workspace to start a new analysis or resume an old one.
**Elements:**
- **Hero/Greeting:** Simple, inviting prompt ("Upload a dataset to begin reasoning.").
- **Upload Zone (`components/Upload/Dropzone.tsx`):** A large, glowing dashed area for CSV uploads.
- **Session Grid (`components/Sessions/SessionGrid.tsx`):** A list/grid of previous sessions (e.g., "Titanic Survival Analysis", "Q3 Sales Logs") displaying the date, row count, and final status.

### `app/session/[id]/page.tsx` - The Active Analysis Workspace
**Purpose:** This is the main application view where the 5-stage pipeline runs. It represents a single uploaded dataset and its corresponding `GAL.json` file.
**Layout Structure:**
- **Left Sidebar (25% width):** The Live GAL Trace (Agent Transitions).
- **Main Content Area (75% width):** The Contextual Visualization Panel (changes based on the active agent).

---

## 3. High-Level Views & Components

### A. Showcasing Agent Transitions: The GAL Trace
**Component File:** `components/GAL/GALFeed.tsx`
**Purpose:** How do we show the `GAL.json` file? The GAL is an append-only memory ledger. We visualize it as a **Live Intelligence Feed** or **Agent Timeline**.
**Behavior:**
- Pinned to the left side of the screen.
- As the backend LangGraph orchestrator moves from agent to agent, new "Blocks" appear in the feed.
- **Visuals:** 
  - `[PENDING]` A pulsing, glowing line showing which agent is currently active (e.g., "🧠 DPSU - Inferring Dataset Identity...").
  - `[COMPLETE]` A solid block containing the summary.
- **Interactivity:** Each block in the GAL feed is clickable. Clicking an older block (e.g., "Data Repair") opens a drawer showing the raw JSON evidence or detailed logs of what exactly was changed.

### B. The Contextual Data Panel (Dynamic Center Area)
**Component File:** `components/Workspace/ContextPanel.tsx`
**Purpose:** As the GAL Trace progresses on the left, the massive center panel drastically changes its UI to visualize the *output* of the current stage.

**Stage Transitions:**
1. **Stage 1: Identity View (`components/Views/DatasetIdentityView.tsx`)**
   - *Active Agent:* DPSU (Dataset Profiler)
   - *Visuals:* Shows inferred real-world domain, a snippet of the data table, and classifications ("Time Series", "E-Commerce").
2. **Stage 2: Integrity View (`components/Views/DataCleaningView.tsx`)**
   - *Active Agent:* DRIL (Data Repair)
   - *Visuals:* "Before vs After" metrics. Big numbers showing "42 Missing Values Imputed", "3 Duplicates Removed".
3. **Stage 3: Exploration View (`components/Views/ExploratoryView.tsx`)**
   - *Active Agent:* EPR (Exploration & Pattern Recognition)
   - *Visuals:* Auto-generated charts (Distributions, Anomaly highlights, Correlation matrices) explained with plain English strings from the AI.

### C. The Most Important View: Human-In-The-Loop Decision Gate
**Component File:** `components/HITL/DecisionGate.tsx`
**Purpose:** EVA is purely analytical up to this point. Now, the IHE (Hypothesis Engine) has generated hypotheses and the system **stops**. It needs human permission to activate the Heavy ML Pipeline.
**Behavior:**
- The UI darkens. A massive, glassmorphism modal locks the screen.
- **Displays:** The generated Hypothesis (e.g., "Sales drop is correlated with the pricing change.").
- **Question:** "Does this dataset require Predictive Machine Learning?"
- **Actions:**
  - `[Approve & Execute ML Pipeline]` (Glowing Orange button)
  - `[Reject / Generate Report Only]` (Outline button)

### D. The ML Pipeline & Final Output View
**Component File:** `components/Views/MachineLearningView.tsx` & `components/Views/FinalReportView.tsx`
**Purpose:** If ML is approved, show the pipeline execution and the final outcome.
- **Visuals:** A 5-step progress bar specifically for the MLRL (Problem Framing -> Candidate Gen -> Training -> Reliability Validating -> Deployment).
- **Final Output:** The Final Decision Report. It displays the top driving factors, risk scores, and the "What should I do now?" plain English recommendations.

---

## 4. Required Component File Tree Summary
When building the UI, structure the files exactly like this:

```text
Frontend/
├── app/
│   ├── page.tsx                     # Landing & Upload
│   ├── session/[id]/page.tsx        # The Main Workspace
│   ├── layout.tsx                   # Dark mode root wrapper
├── components/
│   ├── Upload/
│   │   ├── Dropzone.tsx             # Drag & Drop area
│   ├── GAL/
│   │   ├── GALFeed.tsx              # The scrolling ledger timeline
│   │   ├── GALBlock.tsx             # Individual agent log item
│   ├── Workspace/
│   │   ├── ContextPanel.tsx         # Wrapper that switches views
│   ├── Views/
│   │   ├── DatasetIdentityView.tsx  # Stage 1: Domain & Profiling
│   │   ├── DataCleaningView.tsx     # Stage 2: DRIL fixes
│   │   ├── ExploratoryView.tsx      # Stage 3: Auto-Charts
│   │   ├── FinalReportView.tsx      # Final stage: Output
│   ├── HITL/
│   │   ├── DecisionGate.tsx         # The crucial Approve/Reject Modal
```
