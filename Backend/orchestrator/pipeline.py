import os
import pandas as pd
from typing import Dict, Any, TypedDict, Optional
from langgraph.graph import StateGraph, START, END

from Backend.storage.gal_manager import GALManager
from Backend.models.gal_schema import GlobalAnalysisLedger
from Backend.agents.dpsu_agent import DPSUAgent
from Backend.agents.qbii_agent import QBIIAgent
from Backend.agents.dril_agent import DRILAgent
from Backend.agents.epr_agent import EPRAgent

# Define state strictly mirroring the active analysis instance
class EvaState(TypedDict):
    session_id: str
    csv_file_name: str
    dataframe: Optional[pd.DataFrame]
    gal_ledger: Optional[GlobalAnalysisLedger]
    status: str
    error: Optional[str]

# --- Node Functions ---

def load_data(state: EvaState) -> EvaState:
    try:
        session_id = state["session_id"]
        csv_name = state["csv_file_name"]
        
        snapshot_dir = GALManager.get_dataset_path(session_id, "dataset_snapshot")
        df = pd.read_csv(snapshot_dir / csv_name)
        
        gal = GALManager.read_gal(session_id)
        
        return {**state, "dataframe": df, "gal_ledger": gal, "status": "Loaded Dataset"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed Data Load"}


def run_dpsu(state: EvaState) -> EvaState:
    if state.get("error"): return state
    try:
        identity = DPSUAgent.execute(state["dataframe"])
        gal = state["gal_ledger"]
        gal.dataset_identity = identity
        
        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "Completed DPSU"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed DPSU"}


def run_qbii(state: EvaState) -> EvaState:
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        intent = QBIIAgent.execute(gal.dataset_identity)
        gal.user_intent = intent
        
        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "Completed QBII"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed QBII"}


def run_dril(state: EvaState) -> EvaState:
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        repaired_df, integrity_record = DRILAgent.execute(state["dataframe"], gal.dataset_identity)
        gal.data_integrity = integrity_record
        
        # Write repaired CSV back to isolated directory
        repaired_dir = GALManager.get_dataset_path(state["session_id"], "repaired_dataset")
        repaired_df.to_csv(repaired_dir / state["csv_file_name"], index=False)
        
        GALManager.write_gal(state["session_id"], gal)
        
        # Progress pipeline using the repaired data going forward
        return {**state, "dataframe": repaired_df, "gal_ledger": gal, "status": "Completed DRIL"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed DRIL"}


def run_epr(state: EvaState) -> EvaState:
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        findings = EPRAgent.execute(state["dataframe"], gal.dataset_identity)
        gal.exploratory_findings = findings
        
        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "Phase 1 Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed EPR"}


# --- Build Graph ---

workflow = StateGraph(EvaState)

workflow.add_node("load_data", load_data)
workflow.add_node("run_dpsu", run_dpsu)
workflow.add_node("run_qbii", run_qbii)
workflow.add_node("run_dril", run_dril)
workflow.add_node("run_epr", run_epr)

workflow.add_edge(START, "load_data")
workflow.add_edge("load_data", "run_dpsu")
workflow.add_edge("run_dpsu", "run_qbii")
workflow.add_edge("run_qbii", "run_dril")
workflow.add_edge("run_dril", "run_epr")
workflow.add_edge("run_epr", END)

# Compile into executable application
app = workflow.compile()

def start_phase_1(session_id: str, csv_file_name: str) -> Dict[str, Any]:
    """Helper utility for triggering Phase 1 pipeline externally."""
    initial_state = {
        "session_id": session_id,
        "csv_file_name": csv_file_name,
        "dataframe": None,
        "gal_ledger": None,
        "status": "Initialized",
        "error": None
    }
    
    # Run the synchronous graph invocation
    final_state = app.invoke(initial_state)
    
    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id
    }
