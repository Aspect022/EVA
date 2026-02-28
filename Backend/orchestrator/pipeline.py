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
from Backend.agents.ihe_agent import IHEAgent
from Backend.agents.fie_agent import FIEAgent
from Backend.agents.vpe_agent import VPEAgent
from Backend.agents.adc_agent import ADCAgent
from Backend.agents.rg_agent import RGAgent

# Define state strictly mirroring the active analysis instance
class EvaState(TypedDict):
    session_id: str
    csv_file_name: str
    dataframe: Optional[pd.DataFrame]
    gal_ledger: Optional[GlobalAnalysisLedger]
    status: str
    error: Optional[str]
    rules_mode: Optional[str]

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
        rules_mode = state.get("rules_mode") or "full"
        identity = DPSUAgent.execute(state["dataframe"], rules_mode=rules_mode)
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
        rules_mode = state.get("rules_mode") or "full"
        questions = QBIIAgent.generate_questions(gal.dataset_identity, rules_mode=rules_mode)

        # Write partial intent with only questions populated
        from Backend.models.gal_schema import UserIntentRecord
        partial_intent = UserIntentRecord(
            primary_objective="pending_user_input",
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
        rules_mode = state.get("rules_mode") or "full"
        repaired_df, integrity_record = DRILAgent.execute(
            dataframe=state["dataframe"],
            identity=gal.dataset_identity,
            session_id=state["session_id"],
            csv_file_name=state["csv_file_name"],
            intent=gal.user_intent,
            rules_mode=rules_mode,
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
        rules_mode = state.get("rules_mode") or "full"
        findings = EPRAgent.execute(
            dataframe=state["dataframe"],
            identity=gal.dataset_identity,
            session_id=state["session_id"],
            csv_file_name=state["csv_file_name"],
            intent=gal.user_intent,
            rules_mode=rules_mode,
        )
        gal.exploratory_findings = findings
        
        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "Phase 1 Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed EPR"}


def run_ihe(state: EvaState) -> EvaState:
    """Phase 2: Generate hypotheses from exploratory findings."""
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        rules_mode = state.get("rules_mode") or "full"

        if not gal.exploratory_findings:
            return {**state, "error": "No exploratory findings. Run Phase 1b first.", "status": "Failed IHE"}

        hypotheses_record = IHEAgent.execute(
            identity=gal.dataset_identity,
            findings=gal.exploratory_findings,
            intent=gal.user_intent,
            integrity=gal.data_integrity,
            rules_mode=rules_mode,
        )
        gal.hypotheses = hypotheses_record

        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "Awaiting Hypothesis Review"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed IHE"}


def run_fie(state: EvaState) -> EvaState:
    """Phase 2b: Generate feature engineering plan from RAG and hypotheses."""
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        rules_mode = state.get("rules_mode") or "full"

        if not gal.hypotheses:
            return {**state, "error": "No hypotheses found. Run Phase 2 first.", "status": "Failed FIE"}

        feature_plan = FIEAgent.execute(
            identity=gal.dataset_identity,
            findings=gal.exploratory_findings,
            intent=gal.user_intent,
            integrity=gal.data_integrity,
            hypotheses=gal.hypotheses,
            rules_mode=rules_mode,
        )
        gal.feature_plan = feature_plan

        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "Awaiting Feature Review"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed FIE"}

def run_mlrl(state: EvaState) -> EvaState:
    """Phase 3: Run MLRL pipeline if required."""
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        
        # Check if ML was triggered via user intent
        if not getattr(gal, "ml_required", False):
            return {**state, "status": "ML Not Required"}

        if not gal.feature_plan:
             return {**state, "error": "No feature plan available. Run Phase 2b first.", "status": "Failed MLRL"}

        # Use the latest dataset path tracked by GAL
        csv_path = gal.current_dataset_path
        if csv_path and os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            return {**state, "error": "Dataset not found at current path.", "status": "Failed MLRL"}

        # Extension method mixed into GlobalAnalysisLedger
        gal.run_ml_pipeline()

        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "ML Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed MLRL"}

def run_rg(state: EvaState) -> EvaState:
    """Phase 4: Generate narrative report."""
    if state.get("error"): return state
    try:
        gal = state["gal_ledger"]
        rules_mode = state.get("rules_mode") or "full"

        if not gal.dashboard_plan:
            return {**state, "error": "No dashboard plan found. Run ADC first.", "status": "Failed RG"}

        report_memory = RGAgent.execute(gal, rules_mode=rules_mode)
        gal.report_memory = report_memory

        GALManager.write_gal(state["session_id"], gal)
        return {**state, "gal_ledger": gal, "status": "Report Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed RG"}

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

# Phase 2: IHE hypothesis generation (stops for HITL review)
phase_2_workflow = StateGraph(EvaState)
phase_2_workflow.add_node("run_ihe", run_ihe)

phase_2_workflow.add_edge(START, "run_ihe")
phase_2_workflow.add_edge("run_ihe", END)

phase_2_app = phase_2_workflow.compile()

# Phase 2b: FIE feature engineering plan (stops for HITL review)
phase_2b_workflow = StateGraph(EvaState)
phase_2b_workflow.add_node("run_fie", run_fie)

phase_2b_workflow.add_edge(START, "run_fie")
phase_2b_workflow.add_edge("run_fie", END)

phase_2b_app = phase_2b_workflow.compile()

# Phase 3: Machine Learning & Reinforcement Learning (MLRL)
phase_mlrl_workflow = StateGraph(EvaState)
phase_mlrl_workflow.add_node("run_mlrl", run_mlrl)

phase_mlrl_workflow.add_edge(START, "run_mlrl")
phase_mlrl_workflow.add_edge("run_mlrl", END)

phase_mlrl_app = phase_mlrl_workflow.compile()

# Phase 4: RG narrative report generation
phase_4_workflow = StateGraph(EvaState)
phase_4_workflow.add_node("run_rg", run_rg)

phase_4_workflow.add_edge(START, "run_rg")
phase_4_workflow.add_edge("run_rg", END)

phase_4_app = phase_4_workflow.compile()

def start_phase_1a(session_id: str, csv_file_name: str, rules_mode: str = "full") -> Dict[str, Any]:
    """Phase 1a: Profile dataset + generate user questions. Returns questions."""
    initial_state = {
        "session_id": session_id,
        "csv_file_name": csv_file_name,
        "dataframe": None,
        "gal_ledger": None,
        "status": "Initialized",
        "error": None,
        "rules_mode": rules_mode,
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


def submit_user_answers(session_id: str, answers: Dict[str, str], rules_mode: str = "full") -> Dict[str, Any]:
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
            rules_mode=rules_mode,
        )
        intent.user_confirmed = True
        gal.user_intent = intent
        
        # Machine Learning Activation Gate
        if intent.primary_objective in ["PREDICT", "FORECAST", "ANOMALY_DETECT"]:
            gal.ml_required = True
        else:
            gal.ml_required = False
            
        GALManager.write_gal(session_id, gal)

        return {
            "status": "Intent Confirmed",
            "session_id": session_id,
            "primary_objective": intent.primary_objective,
            "selected_target": intent.selected_target,
        }
    except Exception as e:
        return {"status": "Failed Intent Inference", "error": str(e), "session_id": session_id}


def start_phase_1b(session_id: str, csv_file_name: str, rules_mode: str = "full") -> Dict[str, Any]:
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
        "rules_mode": rules_mode,
    }

    final_state = phase_1b_app.invoke(initial_state)

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
    }


def start_phase_2(session_id: str, rules_mode: str = "full") -> Dict[str, Any]:
    """Phase 2: IHE hypothesis generation. Requires Phase 1b to be complete."""
    gal = GALManager.read_gal(session_id)

    if not gal.exploratory_findings:
        return {
            "status": "Blocked",
            "error": "Exploratory findings not available. Run Phase 1b first.",
            "session_id": session_id,
        }

    # Determine csv_file_name from current_dataset_path
    csv_file_name = ""
    if gal.current_dataset_path:
        csv_file_name = os.path.basename(gal.current_dataset_path)

    initial_state = {
        "session_id": session_id,
        "csv_file_name": csv_file_name,
        "dataframe": None,
        "gal_ledger": gal,
        "status": "Starting Phase 2",
        "error": None,
        "rules_mode": rules_mode,
    }

    final_state = phase_2_app.invoke(initial_state)

    # Extract hypotheses summary for the API response
    hypotheses_summary = []
    result_gal = final_state.get("gal_ledger")
    if result_gal and result_gal.hypotheses and isinstance(result_gal.hypotheses.hypotheses, list):
        for h in result_gal.hypotheses.hypotheses:
            hypotheses_summary.append({
                "observation": h.observation_plain_language,
                "hypothesis": h.hypothesis,
                "plausibility": h.plausibility,
            })

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
        "hypotheses_count": len(hypotheses_summary),
        "hypotheses": hypotheses_summary,
    }


def start_fie(session_id: str, rules_mode: str = "full") -> Dict[str, Any]:
    """Phase 2b: Feature Intelligence Engine gathering RAG domain context. Requires Phase 2 to be complete."""
    gal = GALManager.read_gal(session_id)

    if not gal.hypotheses:
        return {
            "status": "Blocked",
            "error": "Hypotheses not available. Run Phase 2 first.",
            "session_id": session_id,
        }

    # Determine csv_file_name from current_dataset_path
    csv_file_name = ""
    if gal.current_dataset_path:
        csv_file_name = os.path.basename(gal.current_dataset_path)

    initial_state = {
        "session_id": session_id,
        "csv_file_name": csv_file_name,
        "dataframe": None,
        "gal_ledger": gal,
        "status": "Starting Phase 2b",
        "error": None,
        "rules_mode": rules_mode,
    }

    final_state = phase_2b_app.invoke(initial_state)

    # Extract features summary for the API response
    features_summary = []
    result_gal = final_state.get("gal_ledger")
    if result_gal and result_gal.feature_plan and isinstance(result_gal.feature_plan.features, list):
        for f in result_gal.feature_plan.features:
            features_summary.append({
                "name": getattr(f, "name", ""),
                "business_meaning": getattr(f, "business_meaning", ""),
            })

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
        "features_count": len(features_summary),
        "features": features_summary,
    }

def start_mlrl(session_id: str, rules_mode: str = "full") -> Dict[str, Any]:
    """Phase 3: Machine Learning & Reinforcement Learning pipeline."""
    gal = GALManager.read_gal(session_id)

    if not gal.feature_plan:
        return {
            "status": "Blocked",
            "error": "Feature plan not generated. Run Phase 2b first.",
            "session_id": session_id,
        }

    if not getattr(gal, "ml_required", False):
        return {
            "status": "ML Not Required",
            "error": None,
            "session_id": session_id,
        }

    # Determine csv_file_name from current_dataset_path
    csv_file_name = ""
    if gal.current_dataset_path:
        csv_file_name = os.path.basename(gal.current_dataset_path)

    initial_state = {
        "session_id": session_id,
        "csv_file_name": csv_file_name,
        "dataframe": None,
        "gal_ledger": gal,
        "status": "Starting MLRL",
        "error": None,
        "rules_mode": rules_mode,
    }

    final_state = phase_mlrl_app.invoke(initial_state)

    # Extract ML summary
    ml_summary = {}
    result_gal = final_state.get("gal_ledger")
    if result_gal and getattr(result_gal, "model_evaluation", None) and getattr(result_gal.model_evaluation, "selected_model", None):
        model_name = result_gal.model_evaluation.selected_model
        metrics = {}
        if getattr(result_gal.model_evaluation, "results", None):
            metrics = result_gal.model_evaluation.results.get(model_name, {})

        ml_summary = {
            "selected_model": model_name,
            "metrics": metrics,
            "validation_status": getattr(result_gal.model_validation, "validation_status", "UNKNOWN") if getattr(result_gal, "model_validation", None) else "UNKNOWN"
        }

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
        "ml": ml_summary,
    }

def start_vpe(session_id: str, rules_mode: str = "full") -> Dict[str, Any]:
    """VPE: Visualization Planner & Executor. Requires hypotheses to exist (Phase 2 complete)."""
    gal = GALManager.read_gal(session_id)

    if not gal.hypotheses:
        return {
            "status": "Blocked",
            "error": "Hypotheses not generated. Run Phase 2 first.",
            "session_id": session_id,
        }

    if not gal.exploratory_findings:
        return {
            "status": "Blocked",
            "error": "No exploratory findings available.",
            "session_id": session_id,
        }

    # Load the best available dataset (repaired > snapshot)
    try:
        if gal.current_dataset_path and os.path.exists(gal.current_dataset_path):
            df = pd.read_csv(gal.current_dataset_path)
        else:
            csv_file_name = os.path.basename(gal.current_dataset_path) if gal.current_dataset_path else ""
            snapshot_dir = GALManager.get_dataset_path(session_id, "dataset_snapshot").resolve()
            df = pd.read_csv(snapshot_dir / csv_file_name)
    except Exception as e:
        return {
            "status": "Failed VPE",
            "error": f"Could not load dataset: {str(e)}",
            "session_id": session_id,
        }

    try:
        viz_record = VPEAgent.run(
            identity=gal.dataset_identity,
            findings=gal.exploratory_findings,
            session_id=session_id,
            df=df,
            intent=gal.user_intent,
            hypotheses=gal.hypotheses,
            rules_mode=rules_mode,
        )

        gal.visualization_plan = viz_record
        GALManager.write_gal(session_id, gal)

        # Build summary for API response
        viz_summaries = []
        if isinstance(viz_record.visualizations, list):
            for v in viz_record.visualizations:
                if hasattr(v, "model_dump"):
                    viz_summaries.append({
                        "question": v.question,
                        "chart_type": v.chart_type,
                        "validation_result": v.validation_result,
                        "interpretation": v.interpretation,
                    })

        return {
            "status": "VPE Complete",
            "error": None,
            "session_id": session_id,
            "visualizations_count": viz_record.total_rendered,
            "visualizations_failed": viz_record.total_failed,
            "visualizations": viz_summaries,
        }
    except Exception as e:
        return {
            "status": "Failed VPE",
            "error": str(e),
            "session_id": session_id,
        }


def start_adc(session_id: str, rules_mode: str = "full") -> Dict[str, Any]:
    """Phase 3 / ADC: Analytical Dashboard Composer. Requires VPE to exist."""
    gal = GALManager.read_gal(session_id)

    if not gal.visualization_plan:
        return {
            "status": "Blocked",
            "error": "Visualization plan not generated. Run VPE first.",
            "session_id": session_id,
        }

    try:
        dashboard_plan = ADCAgent.execute(
            identity=gal.dataset_identity,
            intent=gal.user_intent,
            findings=gal.exploratory_findings,
            hypotheses=gal.hypotheses,
            viz_plan=gal.visualization_plan,
            rules_mode=rules_mode,
        )

        gal.dashboard_plan = dashboard_plan
        GALManager.write_gal(session_id, gal)

        # Build summary for API response
        return {
            "status": "ADC Complete",
            "error": None,
            "session_id": session_id,
            "panels": len(dashboard_plan.panels) if dashboard_plan.panels else 0,
            "kpis": len(dashboard_plan.kpis) if dashboard_plan.kpis else 0,
            "alerts": len(dashboard_plan.alerts) if dashboard_plan.alerts else 0,
            "recommendations": len(dashboard_plan.recommendations) if dashboard_plan.recommendations else 0,
        }
    except Exception as e:
        return {
            "status": "Failed ADC",
            "error": str(e),
            "session_id": session_id,
        }


def start_rg(session_id: str, rules_mode: str = "full") -> Dict[str, Any]:
    """Phase 4: Report Generator. Requires ADC to exist."""
    gal = GALManager.read_gal(session_id)

    if not gal.dashboard_plan:
        return {
            "status": "Blocked",
            "error": "Dashboard plan not generated. Run ADC first.",
            "session_id": session_id,
        }

    # Determine csv_file_name from current_dataset_path
    csv_file_name = ""
    if gal.current_dataset_path:
        csv_file_name = os.path.basename(gal.current_dataset_path)

    initial_state = {
        "session_id": session_id,
        "csv_file_name": csv_file_name,
        "dataframe": None,
        "gal_ledger": gal,
        "status": "Starting Phase 4 (RG)",
        "error": None,
        "rules_mode": rules_mode,
    }

    final_state = phase_4_app.invoke(initial_state)

    # Extract report summary for the API response
    report_summary = {}
    result_gal = final_state.get("gal_ledger")
    if result_gal and result_gal.report_memory:
        report_summary = {
            "narrative_preview": result_gal.report_memory.narrative[:200] + "..." if result_gal.report_memory.narrative else "",
            "citations_count": len(result_gal.report_memory.citations) if result_gal.report_memory.citations else 0,
            "communicated_recommendations_count": len(result_gal.report_memory.communicated_recommendations) if result_gal.report_memory.communicated_recommendations else 0,
        }

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
        "report": report_summary,
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


# ============================================================================
# LOM PIPELINE — Logging, Monitoring & Observability (Separate from CSV)
# ============================================================================

from Backend.storage.gal_manager import LOMManager
from Backend.agents.lom_parser import LOMParser
from Backend.agents.lom_profiler_agent import LOMProfilerAgent
from Backend.agents.lom_timeline_agent import LOMTimelineAgent
from Backend.agents.lom_rca_agent import LOMRCAAgent
from Backend.agents.lom_report_agent import LOMReportAgent
from Backend.models.lom_schema import (
    SourceInventory, CodeContext, CodeArtifact,
)


# --- LOM State ---

class LOMState(TypedDict):
    session_id: str
    lom_ledger: Optional[Any]
    lom_doc: Optional[Any]
    status: str
    error: Optional[str]


# --- LOM Node Functions ---

def lom_parse_uploads(state: LOMState) -> LOMState:
    """Parse all uploaded LOM files into a LOMDocument."""
    try:
        session_id = state["session_id"]
        upload_dir = LOMManager.get_lom_upload_path(session_id)
        lom_doc = LOMParser.parse_directory(upload_dir)
        ledger = LOMManager.read_lom_gal(session_id)

        # Write Section 1: SourceInventory
        inventory_data = LOMParser.build_source_inventory(lom_doc)
        ledger.source_inventory = SourceInventory(**inventory_data)

        # Write Section 4: CodeContext (from parser directly, no LLM needed)
        if lom_doc.code_artifacts or lom_doc.config_artifacts:
            all_artifacts = lom_doc.code_artifacts + lom_doc.config_artifacts
            ledger.code_context = CodeContext(
                artifacts=all_artifacts,
            )

        LOMManager.write_lom_gal(session_id, ledger)
        return {**state, "lom_doc": lom_doc, "lom_ledger": ledger, "status": "Parsed LOM Uploads"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed LOM Parse"}


def lom_run_profiler(state: LOMState) -> LOMState:
    """Run the LOM Profiler agent to generate log and metric profiles."""
    if state.get("error"):
        return state
    try:
        lom_doc = state["lom_doc"]
        ledger = state["lom_ledger"]

        log_profile, metric_profile = LOMProfilerAgent.execute(lom_doc)

        if log_profile:
            ledger.log_profile = log_profile
        if metric_profile:
            ledger.metric_profile = metric_profile

        LOMManager.write_lom_gal(state["session_id"], ledger)
        return {**state, "lom_ledger": ledger, "status": "LOM Profile Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed LOM Profile"}


def lom_run_timeline(state: LOMState) -> LOMState:
    """Run the LOM Timeline agent to reconstruct events and detect anomalies."""
    if state.get("error"):
        return state
    try:
        lom_doc = state["lom_doc"]
        ledger = state["lom_ledger"]

        timeline, anomalies = LOMTimelineAgent.execute(
            lom_doc=lom_doc,
            log_profile=ledger.log_profile,
            metric_profile=ledger.metric_profile,
            code_context=ledger.code_context,
        )

        if timeline:
            ledger.timeline = timeline
        if anomalies:
            ledger.anomaly_findings = anomalies

        LOMManager.write_lom_gal(state["session_id"], ledger)
        return {**state, "lom_ledger": ledger, "status": "LOM Timeline Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed LOM Timeline"}


def lom_run_rca(state: LOMState) -> LOMState:
    """Run the LOM RCA agent to generate root cause hypotheses."""
    if state.get("error"):
        return state
    try:
        ledger = state["lom_ledger"]
        rca_hypotheses = LOMRCAAgent.execute(ledger)
        ledger.rca_hypotheses = rca_hypotheses

        LOMManager.write_lom_gal(state["session_id"], ledger)
        return {**state, "lom_ledger": ledger, "status": "LOM RCA Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed LOM RCA"}


def lom_run_report(state: LOMState) -> LOMState:
    """Run the LOM Report agent to generate the final RCA narrative."""
    if state.get("error"):
        return state
    try:
        ledger = state["lom_ledger"]
        rca_report = LOMReportAgent.execute(ledger)
        ledger.rca_report = rca_report

        LOMManager.write_lom_gal(state["session_id"], ledger)
        return {**state, "lom_ledger": ledger, "status": "LOM Report Complete"}
    except Exception as e:
        return {**state, "error": str(e), "status": "Failed LOM Report"}


# --- LOM Workflows ---

# LOM Profile: parse uploads + profile logs/metrics
lom_profile_workflow = StateGraph(LOMState)
lom_profile_workflow.add_node("lom_parse_uploads", lom_parse_uploads)
lom_profile_workflow.add_node("lom_run_profiler", lom_run_profiler)
lom_profile_workflow.add_edge(START, "lom_parse_uploads")
lom_profile_workflow.add_edge("lom_parse_uploads", "lom_run_profiler")
lom_profile_workflow.add_edge("lom_run_profiler", END)
lom_profile_app = lom_profile_workflow.compile()

# LOM Analysis: timeline + anomaly detection + RCA
lom_analysis_workflow = StateGraph(LOMState)
lom_analysis_workflow.add_node("lom_run_timeline", lom_run_timeline)
lom_analysis_workflow.add_node("lom_run_rca", lom_run_rca)
lom_analysis_workflow.add_edge(START, "lom_run_timeline")
lom_analysis_workflow.add_edge("lom_run_timeline", "lom_run_rca")
lom_analysis_workflow.add_edge("lom_run_rca", END)
lom_analysis_app = lom_analysis_workflow.compile()

# LOM Report: generate final narrative
lom_report_workflow = StateGraph(LOMState)
lom_report_workflow.add_node("lom_run_report", lom_run_report)
lom_report_workflow.add_edge(START, "lom_run_report")
lom_report_workflow.add_edge("lom_run_report", END)
lom_report_app = lom_report_workflow.compile()


# --- LOM Public Functions ---

def start_lom_profile(session_id: str) -> Dict[str, Any]:
    """LOM Phase 1: Parse uploads + profile logs/metrics."""
    # Ensure LOM session exists
    try:
        LOMManager.read_lom_gal(session_id)
    except FileNotFoundError:
        LOMManager.create_lom_session(session_id)

    initial_state: LOMState = {
        "session_id": session_id,
        "lom_ledger": None,
        "lom_doc": None,
        "status": "Starting LOM Profile",
        "error": None,
    }

    final_state = lom_profile_app.invoke(initial_state)

    # Build response
    ledger = final_state.get("lom_ledger")
    source_summary = {}
    if ledger and ledger.source_inventory:
        source_summary = {
            "total_files": ledger.source_inventory.total_files,
            "total_log_entries": ledger.source_inventory.total_log_entries,
            "total_metric_points": ledger.source_inventory.total_metric_points,
            "total_code_artifacts": ledger.source_inventory.total_code_artifacts,
        }

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
        "source_inventory": source_summary,
    }


def start_lom_timeline(session_id: str) -> Dict[str, Any]:
    """LOM Phase 2: Timeline reconstruction + anomaly detection + RCA."""
    try:
        ledger = LOMManager.read_lom_gal(session_id)
    except FileNotFoundError:
        return {"status": "Blocked", "error": "LOM session not found. Run lom-profile first.", "session_id": session_id}

    if not ledger.log_profile and not ledger.metric_profile and not ledger.source_inventory:
        return {"status": "Blocked", "error": "No profile data. Run lom-profile first.", "session_id": session_id}

    # Reload the parsed LOM data for timeline agent
    upload_dir = LOMManager.get_lom_upload_path(session_id)
    lom_doc = LOMParser.parse_directory(upload_dir)

    initial_state: LOMState = {
        "session_id": session_id,
        "lom_ledger": ledger,
        "lom_doc": lom_doc,
        "status": "Starting LOM Analysis",
        "error": None,
    }

    final_state = lom_analysis_app.invoke(initial_state)

    result_ledger = final_state.get("lom_ledger")
    hypotheses_summary = []
    if result_ledger and result_ledger.rca_hypotheses:
        for h in result_ledger.rca_hypotheses.hypotheses:
            hypotheses_summary.append({
                "hypothesis": h.hypothesis,
                "category": h.category,
                "plausibility": h.plausibility,
            })

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
        "timeline_events": result_ledger.timeline.total_events if result_ledger and result_ledger.timeline else 0,
        "anomalies_found": result_ledger.anomaly_findings.total_anomalies if result_ledger and result_ledger.anomaly_findings else 0,
        "hypotheses_count": len(hypotheses_summary),
        "hypotheses": hypotheses_summary,
    }


def start_lom_rca(session_id: str) -> Dict[str, Any]:
    """LOM standalone RCA — run only the RCA agent (if timeline already exists)."""
    try:
        ledger = LOMManager.read_lom_gal(session_id)
    except FileNotFoundError:
        return {"status": "Blocked", "error": "LOM session not found.", "session_id": session_id}

    if not ledger.timeline and not ledger.anomaly_findings:
        return {"status": "Blocked", "error": "No timeline/anomaly data. Run lom-timeline first.", "session_id": session_id}

    rca_hypotheses = LOMRCAAgent.execute(ledger)
    ledger.rca_hypotheses = rca_hypotheses
    LOMManager.write_lom_gal(session_id, ledger)

    hypotheses_summary = []
    for h in rca_hypotheses.hypotheses:
        hypotheses_summary.append({
            "hypothesis": h.hypothesis,
            "category": h.category,
            "plausibility": h.plausibility,
            "evidence_count": len(h.evidence_chain),
        })

    return {
        "status": "LOM RCA Complete",
        "error": None,
        "session_id": session_id,
        "primary_suspect": rca_hypotheses.primary_suspect,
        "hypotheses_count": len(hypotheses_summary),
        "hypotheses": hypotheses_summary,
    }


def start_lom_report(session_id: str) -> Dict[str, Any]:
    """LOM Phase 3: Generate final RCA narrative report."""
    try:
        ledger = LOMManager.read_lom_gal(session_id)
    except FileNotFoundError:
        return {"status": "Blocked", "error": "LOM session not found.", "session_id": session_id}

    if not ledger.rca_hypotheses:
        return {"status": "Blocked", "error": "No RCA hypotheses. Run lom-timeline first.", "session_id": session_id}

    initial_state: LOMState = {
        "session_id": session_id,
        "lom_ledger": ledger,
        "lom_doc": None,
        "status": "Starting LOM Report",
        "error": None,
    }

    final_state = lom_report_app.invoke(initial_state)

    result_ledger = final_state.get("lom_ledger")
    report_summary = {}
    if result_ledger and result_ledger.rca_report:
        report_summary = {
            "executive_summary": result_ledger.rca_report.executive_summary[:300],
            "root_cause_preview": result_ledger.rca_report.root_cause[:200] + "..." if result_ledger.rca_report.root_cause else "",
            "remediation_count": len(result_ledger.rca_report.remediation_steps),
            "confidence_level": result_ledger.rca_report.confidence_level,
        }

    return {
        "status": final_state["status"],
        "error": final_state.get("error"),
        "session_id": session_id,
        "report": report_summary,
    }

