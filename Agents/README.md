# Agents - EVA Data Science OS

This directory contains metadata and related documentation or wrappers for the AI Specialist Agents and their associated skills used by the EVA project framework.

## Overview
While the actual execution code for analytical agents (like DPSU, QBII, DRIL) resides in [`../Backend/agents/`](../Backend/agents/), this folder serves as a structural placeholder for agent configurations and Antigravity Kit agent guidelines.

## Structure
- Specific reasoning capabilities are mapped to different agent definitions in the `.agent/` hidden folder at the project root.
- The `Backend/agents/` folder contains the Python implementations for the execution pipeline.

## Active Specialists 
Core orchestration relies on specialized behaviors:
- **Backend Specialist**: Handles data repair, API building, and pipeline execution.
- **Frontend Specialist**: Develops the React and Streamlit interfaces.
- **Project Planner**: Maintains architectural and planned states.

For more information, see the root architectural guidelines.
