# PLAN-eva-ui-design

## Overview
EVA is an autonomous data science assistant (a reasoning OS). As per Phase 4 of the architectural roadmap, we are building the final React + Next.js frontend to replace the temporary Streamlit UI. The UI must support dataset uploads, live Global Analysis Ledger (GAL) reasoning traces, and a Human-In-The-Loop (HITL) intervention gate for hypothesis validation. This plan focuses on creating wireframes first via Google Stitch, followed by the Next.js implementation.

## Project Type
WEB

## Success Criteria
- [ ] Wireframes generated and approved by user.
- [ ] Next.js app initialized with Tailwind CSS and the recommended design system.
- [ ] UI correctly visualizes a dummy/mock GAL trace and dataset overview.
- [ ] Human-In-The-Loop (HITL) prompt component is fully implemented.

## Tech Stack
- **Framework:** Next.js (React)
- **Styling:** Tailwind CSS (Dark Mode, OLED style as per `ui-ux-pro-max`)
- **Typography:** Fira Code / Fira Sans
- **Design System Rules:** Deep black backgrounds, primary `#3B82F6`, CTA `#F97316`, SVG icons (Lucide), `cursor-pointer`, smooth hover states, >4.5:1 contrast.

## File Structure
```text
Frontend/
├── app/
│   ├── page.tsx (Dashboard + Upload)
│   ├── layout.tsx
│   ├── globals.css
├── components/
│   ├── Sidebar.tsx
│   ├── GALTrace.tsx (Live Reasoning terminal/feed)
│   ├── DataVisualizations.tsx (Table, Charts)
│   ├── HITLPrompt.tsx (Human in the loop intervention card)
├── lib/
│   ├── utils.ts
├── tailwind.config.ts
```

## Task Breakdown

### Task 1: Initialize Next.js Dashboard
- **Agent:** `frontend-specialist`
- **Skills:** `app-builder`, `frontend-design`
- **INPUT:** Empty `Frontend/` minus Streamlit files.
- **OUTPUT:** Next.js project with Tailwind, Lucide React, and Fira typography.
- **VERIFY:** `npm run dev` starts successfully with the dark theme applied.

### Task 2: Build Main Layout & Navigation
- **Agent:** `frontend-specialist`
- **Skills:** `frontend-design`
- **INPUT:** Next.js scaffolding.
- **OUTPUT:** Persistent left sidebar and main dark-mode container.
- **VERIFY:** Layout renders cleanly on desktop (1024px+).

### Task 3: Implement GAL Trace Component
- **Agent:** `frontend-specialist`
- **Skills:** `clean-code`
- **INPUT:** Layout component.
- **OUTPUT:** A scrolling, terminal-like or timeline component displaying AI reasoning steps.
- **VERIFY:** Component handles mock expanding data strings without layout shifts.

### Task 4: Implement HITL Decision Gate
- **Agent:** `frontend-specialist`
- **Skills:** `frontend-design`
- **INPUT:** Dashboard layout.
- **OUTPUT:** A prominent card/modal that asks the user to accept/reject a hypothesis to unlock ML execution.
- **VERIFY:** Clicking 'Approve' or 'Reject' triggers a mock state change.

## Phase X: Verification
- [ ] `npm run build` succeeds
- [ ] Security scan passes
- [ ] UX Audit (`ux_audit.py`) passes
- [ ] No purple/violet hex codes used
- [ ] Socratic Gate respected
