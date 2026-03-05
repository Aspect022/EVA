# Documentation - EVA Data Science OS

This directory serves as the central repository for all architectural decisions, design documents, phase tracking, and guides for the EVA Data Science OS.

## Directory Structure

| Document / Folder | Description |
|-------------------|-------------|
| `EVA-DataScience/` | Detailed mini-docs covering Phase 1 and Phase 2 data science agents (DPSU, QBII, DRIL, IHE, etc.). |
| `EVA-ML/` | Documentation relating to the Machine Learning Reasoning Layer (MLRL) and automated modeling decisions. |
| `Frontend_UI_Architecture.md` | React implementation plans, component structural requirements, and state management strategies. |
| `TechStack.md` | An overview of the libraries, frameworks, and technologies utilized across the stack. |
| `PLAN-*` files | Iterative planning files for features like RAG integration, report generation, or config execution fixes. |
| `EVA DataScience - Complete Docs.md` | Aggregated or high-level overview of the entire analytical capability suite. |

## AI-Friendly Documentation
To ensure AI assistants can easily parse the intent of the project, refer to the `Implementation_Tracker.md` at the root for a broad overview before diving into the individual mini-docs located here.

## How to Contribute
When proposing architectural changes or new agent phases:
1. Create a `PLAN-{feature}.md` file here for review.
2. Outline the reasoning strictly separating UI design logic from Backend GAL-writing logic.
3. Update `TechStack.md` if introducing new libraries.

## License
MIT
