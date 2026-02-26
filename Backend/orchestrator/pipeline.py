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
        
        snapshot_dir = GALManager.get_dataset_path(session_id, "dataset_snapshot").resolve()
        df = pd.read_csv(snapshot_dir / csv_name)
        
        gal = GALManager.read_gal(session_id)

        # Track the current dataset path in the GAL
        gal.current_dataset_path = str(snapshot_dir / csv_name)
        GALManager.write_gal(session_id, gal)
        
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


def run_qbii_generate(state: EvaState) -> EvaState:
    """Phase A of QBII: generate questions and pause for user input."""
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        questions = QBIIAgent.generate_questions(gal.dataset_identity)

        # Write partial intent with only questions populated
        from Backend.models.gal_schema import UserIntentRecord
        partial_intent = UserIntentRecord(
            analytical_goal="pending_user_input",
            decision_supported="pending_user_input",
            stakeholder_type="pending_user_input",
            interpretability_priority="pending_user_input",
            constraints=[],
            generated_questions=questions,
            user_confirmed=False,
        )
        gal.user_intent = partial_intent
        GALManager.write_gal(state["session_id"], gal)

        return {**state, "gal_ledger": gal, "status": "Awaiting User Intent"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed QBII"}


def run_dril(state: EvaState) -> EvaState:
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        repaired_df, integrity_record = DRILAgent.execute(
            dataframe=state["dataframe"],
            identity=gal.dataset_identity,
            session_id=state["session_id"],
            csv_file_name=state["csv_file_name"],
            intent=gal.user_intent,
        )
        gal.data_integrity = integrity_record

        # Update the current dataset path to the repaired version
        repaired_path = GALManager.get_dataset_path(state["session_id"], "repaired_dataset").resolve()
        gal.current_dataset_path = str(repaired_path / state["csv_file_name"])
        
        GALManager.write_gal(state["session_id"], gal)
        
        return {**state, "dataframe": repaired_df, "gal_ledger": gal, "status": "Completed DRIL"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed DRIL"}


def run_epr(state: EvaState) -> EvaState:
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        findings = EPRAgent.execute(
            dataframe=state["dataframe"],
            identity=gal.dataset_identity,
            session_id=state["session_id"],
            csv_file_name=state["csv_file_name"],
            intent=gal.user_intent,
        )
        gal.exploratory_findings = findings
        
        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "Phase 1 Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed EPR"}


# --- Build Graphs ---

# Phase 1a: DPSU + QBII question generation (stops for user input)
phase_1a_workflow = StateGraph(EvaState)
phase_1a_workflow.add_node("load_data", load_data)
phase_1a_workflow.add_node("run_dpsu", run_dpsu)
phase_1a_workflow.add_node("run_qbii_generate", run_qbii_generate)

phase_1a_workflow.add_edge(START, "load_data")
phase_1a_workflow.add_edge("load_data", "run_dpsu")
phase_1a_workflow.add_edge("run_dpsu", "run_qbii_generate")
phase_1a_workflow.add_edge("run_qbii_generate", END)

phase_1a_app = phase_1a_workflow.compile()

# Phase 1b: DRIL + EPR (runs after user answers questions)
phase_1b_workflow = StateGraph(EvaState)
phase_1b_workflow.add_node("run_dril", run_dril)
phase_1b_workflow.add_node("run_epr", run_epr)

phase_1b_workflow.add_edge(START, "run_dril")
phase_1b_workflow.add_edge("run_dril", "run_epr")
phase_1b_workflow.add_edge("run_epr", END)

phase_1b_app = phase_1b_workflow.compile()


def start_phase_1a(session_id: str, csv_file_name: str) -> Dict[str, Any]:
    """Phase 1a: Profile dataset + generate user questions. Returns questions."""
    initial_state = {
        "session_id": session_id,
        "csv_file_name": csv_file_name,
        "dataframe": None,
        "gal_ledger": None,
        "status": "Initialized",
        "error": None,
    }
    
    final_state = phase_1a_app.invoke(initial_state)
    
    # Extract generated questions for the API response
    questions = []
    gal = final_state.get("gal_ledger")
    if gal and gal.user_intent and gal.user_intent.generated_questions:
        questions = [
            {
                "question": q.question,
                "question_type": q.question_type,
                "why_asked": q.why_asked,
            }
            for q in gal.user_intent.generated_questions
        ]
    
    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
        "questions": questions,
    }


def submit_user_answers(session_id: str, answers: Dict[str, str]) -> Dict[str, Any]:
    """Phase 1 bridge: user submits answers -> QBII infers intent."""
    try:
        gal = GALManager.read_gal(session_id)

        if not gal.dataset_identity:
            raise ValueError("No dataset identity found. Run Phase 1a first.")
        if not gal.user_intent or not gal.user_intent.generated_questions:
            raise ValueError("No questions found. Run Phase 1a first.")

        intent = QBIIAgent.infer_intent(
            identity=gal.dataset_identity,
            questions=gal.user_intent.generated_questions,
            user_answers=answers,
        )
        intent.user_confirmed = True
        gal.user_intent = intent
        GALManager.write_gal(session_id, gal)

        return {
            "status": "Intent Confirmed",
            "session_id": session_id,
            "analytical_goal": intent.analytical_goal,
            "selected_target": intent.selected_target,
        }
    except Exception as e:
        return {"status": "Failed Intent Inference", "error": str(e), "session_id": session_id}


def start_phase_1b(session_id: str, csv_file_name: str) -> Dict[str, Any]:
    """Phase 1b: Data repair + Exploration. Requires user intent to exist."""
    gal = GALManager.read_gal(session_id)

    if not gal.user_intent or not gal.user_intent.user_confirmed:
        return {
            "status": "Blocked",
            "error": "User intent not confirmed. Submit answers first.",
            "session_id": session_id,
        }

    # Load the dataframe from snapshot
    snapshot_dir = GALManager.get_dataset_path(session_id, "dataset_snapshot").resolve()
    csv_path = snapshot_dir / csv_file_name
    df = pd.read_csv(csv_path)

    initial_state = {
        "session_id": session_id,
        "csv_file_name": csv_file_name,
        "dataframe": df,
        "gal_ledger": gal,
        "status": "Starting Phase 1b",
        "error": None,
    }

    final_state = phase_1b_app.invoke(initial_state)

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
    }


# Legacy compatibility — runs full pipeline without HITL pause
def start_phase_1(session_id: str, csv_file_name: str) -> Dict[str, Any]:
    """Full Phase 1 without user interaction (backward compatible)."""
    result_a = start_phase_1a(session_id, csv_file_name)
    if result_a.get("error"):
        return result_a

    # Auto-submit empty answers (LLM will infer from dataset context)
    submit_user_answers(session_id, {})

    result_b = start_phase_1b(session_id, csv_file_name)
    return result_b
