# UI Design System: EVA React Migration
## 🎨 DESIGN COMMITMENT: "Technical Elegance"
- **Topological Choice:** Fragmented dashboard layout with a floating collapsable navigation and persistent Global Agentic Ledger (GAL) tracker at the bottom/side. Landing page avoids the standard split, using an immersive dark field with the brain visualization as an interactive centerpiece.
- **Risk Factor:** No top navbar on the landing page, relying completely on the floating dock for navigation. Dense, data-heavy dashboard with specialized agent zones.
- **Readability Conflict:** Maintaining high contrast with the dark theme and vibrant UI accents.
- **Cliché Liquidation:** No Bento Grids. No standard blue-on-white SaaS panels. Using the specific cosmic/deep-ocean palette provided.

## 1. Color Palette (Strictly Enforced)
We are using the provided celestial/deep-ocean theme:
- **Ink Black** (`#0d1b2aff`): Main application background, deeply immersive.
- **Prussian Blue** (`#1b263bff`): Secondary background for cards, modals, and the GAL console.
- **Dusk Blue** (`#415a77ff`): Borders, subtle active states, muted text.
- **Dusty Denim** (`#778da9ff`): Secondary text, inactive icons, subtle highlights.
- **Alabaster Grey** (`#e0e1ddff`): Primary text, strong highlights, glowing elements.
- *Accent/Glows*: We will use the brain's neon cyan/purple strictly for data visualization and agent active states.

## 2. Typography
- **Primary Font**: `Inter` or `Geist` (clean, technical, readable at small sizes).
- **Secondary/Code Font**: `JetBrains Mono` for agent outputs, data parameters, and the GAL console.
- **Styling**: Massive, brutalist typography for the Hero ("AUTONOMOUS DATA SCIENCE.").

## 3. Layout Rules
- **Landing Page**: Full viewport height, absolute center alignment, deep space background, glowing brain interactive element. No traditional header.
- **Dashboard**:
  - Left: Collapsable slim navigation.
  - Top Work Area: Active agent visualizer ("Next Agent") and specific tools.
  - Center Work Area: Dynamic loaded content (Upload, Question Builder, Visualizations).
  - Bottom/Embedded: The GAL (Global Agentic Ledger) console showing step-by-step progress.

---

# PLAN-react-migration.md

## Overview & Success Criteria
- **Goal:** Migrate `streamlit_app.py` to a full Next.js/React frontend with Tailwind CSS mapping the 10-step agent pipeline.
- **Project Type:** WEB.
- **Success Criteria:** 
  1. Complete removal of Streamlit logic, routing entirely through `Backend/session.py`.
  2. Implement the Landing view exactly as wireframed.
  3. Implement the Dashboard view showing navigation, GAL pipeline, and active agent stages (DPSU, QBII, DRIL, etc.).
  4. Ensure precise application of the custom color variables.

## Tech Stack
- **Framework:** Next.js (App Router) + React (Client/Server components)
- **Styling:** Tailwind CSS using the exact provided color variables.
- **State Management:** Local React state and Context API to pass Session IDs and GAL updates.
- **Data Fetching:** Standard `fetch` API against the FastAPI backend endpoints.

## File Structure (React_Based)
```
Frontend/React_Based/
├── app/
│   ├── page.tsx            # Landing Page Hero + Brain visualization
│   ├── dashboard/          # App Shell (Collapsable Nav, GAL tracker)
│   │   ├── page.tsx        # Dashboard work area rendering dynamic steps
│   │   └── layout.tsx      # Sidebar + Next Agent Header
├── components/
│   ├── ui/                 # Reusable buttons, cards, docks (Tailwind styled)
│   ├── pipeline/           # Specific components for each agent step
│   │   ├── DatasetUpload.tsx
│   │   ├── QuestionBuilder.tsx   # For QBII (Answer EVA's Questions)
│   │   ├── DashboardRenderer.tsx # For ADC/IHE visuals
│   │   ├── FIEPlanConsole.tsx    # For Feature Engineering output
│   │   └── ReportViewer.tsx      # For Final RG output
│   └── gal/
│       └── GlobalAgenticLedger.tsx # 1->2->3 tracker and console
└── styles/
    └── globals.css         # Define CSS variables (--ink-black, etc.)
```

## Task Breakdown

### TASK 1: Setup Global CSS and UI Architecture
- **Agent/Skill:** `frontend-specialist`, `tailwind-patterns`
- **Input:** Global colors provided by user.
- **Output:** `globals.css` with CSS variables. Custom base Tailwnd classes for borders/glass effects using the palette.
- **Verify:** `globals.css` correctly maps `--ink-black`, `--prussian-blue`, etc.

### TASK 2: Implement Landing Page & Dock
- **Agent/Skill:** `frontend-specialist`, `web-design-guidelines`
- **Input:** Wireframe 1.
- **Output:** `app/page.tsx`, `components/hero.tsx` with floating dock and "Start Free Trial" CTA. Brain image is centered on the layout.
- **Verify:** Check mobile and desktop responsiveness. No top nav visible.

### TASK 3: Dashboard Layout (Shell & Sidebar)
- **Agent/Skill:** `frontend-specialist`, `react-best-practices`
- **Input:** Wireframe 2, 3.
- **Output:** `app/dashboard/layout.tsx`. Left collapsable sidebar. "Next Agent" top-right widget.
- **Verify:** Sidebar expands and collapses smoothly.

### TASK 4: Global Agentic Ledger (GAL) Component
- **Agent/Skill:** `frontend-specialist`
- **Input:** Wireframe 2 below content block.
- **Output:** `components/gal/GlobalAgenticLedger.tsx`. Takes prop `current_step` (1 to 10). Renders `1 -> 2 -> 3...` tracker and console output showing previous GAL data.
- **Verify:** Progress steps UI renders clearly.

### TASK 5: Dashboard Work Area (Upload & Question Builder)
- **Agent/Skill:** `frontend-specialist`, `app-builder`
- **Input:** Wireframe 3 (Upload), Wireframe 4 (Question Builder)
- **Output:** `app/dashboard/page.tsx` integrating `DatasetUpload.tsx` and `QuestionBuilder.tsx`. Handle state when session starts, dataset is uploaded, and QBII returns questions.
- **Verify:** Click upload triggers file selection; Questions correctly map into A, B, C, D cards.

### TASK 6: Pipeline Execution & Visualization Views
- **Agent/Skill:** `frontend-specialist`
- **Input:** Streamlit app's ADC, IHE, FIE, RG sections.
- **Output:** Components to render charts, code, and Markdown output dynamically fetched from `/session/{id}/execute/*` endpoints.
- **Verify:** Fetching logic correctly updates the UI and GAL.

## Phase X: Verification
- [ ] Lint: `npm run lint` & type safety checks pass.
- [ ] UX Audit: High contrast ratio between Alabaster Grey and Ink Black.
- [ ] API Connection: The Next.js app communicates flawlessly with `localhost:8000/session/...`.

## ✅ PHASE X COMPLETE
*(To be completed after execution)*
