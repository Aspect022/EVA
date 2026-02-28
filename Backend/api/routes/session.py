import uuid
import shutil
import os
import time
import json
import asyncio
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from Backend.storage.gal_manager import GALManager, LOMManager
from Backend.storage.dataset_registry import DatasetRegistry
from Backend.orchestrator.pipeline import (
    start_phase_1, start_phase_1a, start_phase_1b, submit_user_answers,
    start_phase_2, start_fie, start_mlrl, start_vpe, start_adc, start_rg,
    start_lom_profile, start_lom_timeline, start_lom_rca, start_lom_report,
)

import traceback
from typing import Optional, Dict, List, Any

router = APIRouter()

class SessionResponse(BaseModel):
    session_id: str
    message: str

class SessionInfo(BaseModel):
    session_id: str
    has_identity: bool = False
    has_intent: bool = False
    has_integrity: bool = False
    has_findings: bool = False
    has_hypotheses: bool = False
    has_features: bool = False
    has_mlrl: bool = False
    has_visualizations: bool = False
    has_dashboard: bool = False
    has_report: bool = False
    csv_file: Optional[str] = None
    # LOM progress tracking
    has_lom_data: bool = False
    has_lom_profile: bool = False
    has_lom_timeline: bool = False
    has_lom_rca: bool = False
    has_lom_report: bool = False
    lom_file_count: int = 0

@router.get("/list", response_model=List[SessionInfo])
def list_sessions():
    """Lists all existing sessions with their pipeline progress."""
    sessions_dir = Path("eva_sessions")
    if not sessions_dir.exists():
        return []
    results = []
    for entry in sorted(sessions_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not entry.is_dir():
            continue
        gal_path = entry / "GAL.json"
        if not gal_path.exists():
            continue
        try:
            gal = GALManager.read_gal(entry.name)
            csv_file = None
            snapshot_dir = entry / "dataset_snapshot"
            if snapshot_dir.exists():
                csvs = [f.name for f in snapshot_dir.iterdir() if f.suffix == ".csv"]
                if csvs:
                    csv_file = csvs[0]

            # LOM progress
            has_lom_data = False
            has_lom_profile = False
            has_lom_timeline = False
            has_lom_rca = False
            has_lom_report = False
            lom_file_count = 0

            lom_gal_path = entry / "LOM_GAL.json"
            if lom_gal_path.exists():
                try:
                    lom_gal = LOMManager.read_lom_gal(entry.name)
                    has_lom_data = lom_gal.source_inventory is not None
                    has_lom_profile = lom_gal.log_profile is not None or lom_gal.metric_profile is not None
                    has_lom_timeline = lom_gal.timeline is not None
                    has_lom_rca = lom_gal.rca_hypotheses is not None
                    has_lom_report = lom_gal.rca_report is not None
                    if lom_gal.source_inventory:
                        lom_file_count = lom_gal.source_inventory.total_files
                except Exception:
                    pass

            results.append(SessionInfo(
                session_id=entry.name,
                has_identity=gal.dataset_identity is not None,
                has_intent=gal.user_intent is not None and gal.user_intent.user_confirmed,
                has_visualizations=gal.visualization_plan is not None,
                has_features=gal.feature_plan is not None,
                has_integrity=gal.data_integrity is not None,
                has_findings=gal.exploratory_findings is not None,
                has_hypotheses=gal.hypotheses is not None,
                has_mlrl=getattr(gal, "candidate_models", None) is not None,
                has_dashboard=gal.dashboard_plan is not None,
                has_report=gal.report_memory is not None,
                csv_file=csv_file,
                has_lom_data=has_lom_data,
                has_lom_profile=has_lom_profile,
                has_lom_timeline=has_lom_timeline,
                has_lom_rca=has_lom_rca,
                has_lom_report=has_lom_report,
                lom_file_count=lom_file_count,
            ))
        except Exception:
            results.append(SessionInfo(session_id=entry.name))
    return results

@router.post("/create", response_model=SessionResponse)
def create_session():
    """Step 0: Initialize empty analysis universe."""
    session_id = str(uuid.uuid4())
    try:
        GALManager.create_session(session_id)
        return SessionResponse(session_id=session_id, message="Session initialized. Pending dataset.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/upload")
def upload_dataset(session_id: str, file: UploadFile = File(...)):
    """Uploads CSV to the designated session."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV datasets are currently supported in Phase 1.")
        
    try:
        gal = GALManager.read_gal(session_id)
        snapshot_dir = GALManager.get_dataset_path(session_id, "dataset_snapshot")
        save_path = snapshot_dir / file.filename
        
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Register dataset in the registry for Quick Mode
        DatasetRegistry.register(
            file_path=save_path,
            filename=file.filename,
            size_bytes=save_path.stat().st_size,
            session_id=session_id,
            completed_phases=[],
        )
            
        return {"filename": file.filename, "status": "uploaded", "session_id": session_id}
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Phase 1a: Profile + Generate Questions ---

class Phase1aResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    questions: List[Dict] = []

@router.post("/{session_id}/execute/phase1a", response_model=Phase1aResponse)
def execute_phase_1a(session_id: str, csv_file_name: str, rules_mode: str = "full"):
    """Runs DPSU + QBII question generation. Returns questions for the user."""
    try:
        result = start_phase_1a(session_id, csv_file_name, rules_mode=rules_mode)
        DatasetRegistry.update_phases(session_id, ["phase1a"])
        return Phase1aResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- Submit User Answers ---

class UserAnswersRequest(BaseModel):
    answers: Dict[str, str]

class IntentResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    primary_objective: Optional[str] = None
    selected_target: Optional[str] = None

@router.post("/{session_id}/submit-answers", response_model=IntentResponse)
def submit_answers(session_id: str, body: UserAnswersRequest, rules_mode: str = "full"):
    """Submit user answers to QBII questions. Infers and confirms intent."""
    try:
        result = submit_user_answers(session_id, body.answers, rules_mode=rules_mode)
        DatasetRegistry.update_phases(session_id, ["phase1a", "answers"])
        return IntentResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- Phase 1b: Repair + Exploration ---

class ExecuteResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None

@router.post("/{session_id}/execute/phase1b", response_model=ExecuteResponse)
def execute_phase_1b(session_id: str, csv_file_name: str, rules_mode: str = "full"):
    """Runs DRIL + EPR after user intent is confirmed."""
    try:
        result = start_phase_1b(session_id, csv_file_name, rules_mode=rules_mode)
        DatasetRegistry.update_phases(session_id, ["phase1a", "answers", "phase1b"])
        return ExecuteResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- Legacy: Full Phase 1 (no HITL) ---

@router.post("/{session_id}/execute")
def execute_pipeline(session_id: str, csv_file_name: str):
    """Triggers the full Phase 1 pipeline (backward compatible, no user interaction)."""
    try:
        result = start_phase_1(session_id, csv_file_name)
        return ExecuteResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- GAL Retrieval ---

@router.get("/{session_id}/gal")
def get_gal(session_id: str):
    """Retrieves the current state of the Global Analysis Ledger."""
    try:
        gal = GALManager.read_gal(session_id)
        return gal.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}/visualizations")
def get_visualizations(session_id: str):
    """Retrieves full visualization data including Plotly configs for frontend rendering."""
    try:
        gal = GALManager.read_gal(session_id)
        if not gal.visualization_plan:
            return {"visualizations": [], "total_rendered": 0, "total_failed": 0, "overall_reasoning": ""}

        viz_data = []
        for v in (gal.visualization_plan.visualizations or []):
            if hasattr(v, "model_dump"):
                viz_data.append(v.model_dump())
            elif isinstance(v, dict):
                viz_data.append(v)

        return {
            "visualizations": viz_data,
            "total_rendered": gal.visualization_plan.total_rendered,
            "total_failed": gal.visualization_plan.total_failed,
            "total_planned": gal.visualization_plan.total_planned,
            "overall_reasoning": gal.visualization_plan.overall_reasoning,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}/dashboard")
def get_dashboard(session_id: str):
    """Retrieves full dashboard data including KPIs, alerts, recommendations, and panels."""
    try:
        gal = GALManager.read_gal(session_id)
        if not gal.dashboard_plan:
            return {"kpis": [], "alerts": [], "recommendations": [], "panels": [], "overall_reasoning": ""}

        dp = gal.dashboard_plan
        return {
            "kpis": [k.model_dump() if hasattr(k, "model_dump") else k for k in (dp.kpis or [])],
            "alerts": [a.model_dump() if hasattr(a, "model_dump") else a for a in (dp.alerts or [])],
            "recommendations": [r.model_dump() if hasattr(r, "model_dump") else r for r in (dp.recommendations or [])],
            "panels": [p.model_dump() if hasattr(p, "model_dump") else p for p in (dp.panels or [])],
            "stakeholder_calibration": dp.stakeholder_calibration,
            "overall_reasoning": dp.overall_reasoning,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}/report")
def get_report(session_id: str):
    """Retrieves the full narrative report."""
    try:
        gal = GALManager.read_gal(session_id)
        if not gal.report_memory:
            return {"narrative": "", "citations": [], "communicated_recommendations": []}

        rm = gal.report_memory
        return {
            "narrative": rm.narrative,
            "citations": rm.citations or [],
            "included_visualizations": rm.included_visualizations or [],
            "communicated_recommendations": rm.communicated_recommendations or [],
            "stakeholder_calibration": rm.stakeholder_calibration,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Phase 2: IHE Hypothesis Generation ---

class Phase2Response(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    hypotheses_count: int = 0
    hypotheses: List[Dict] = []

@router.post("/{session_id}/execute/phase2", response_model=Phase2Response)
def execute_phase_2(session_id: str, rules_mode: str = "full"):
    """Runs IHE: generates hypotheses from exploratory findings. Returns hypotheses for HITL review."""
    try:
        result = start_phase_2(session_id, rules_mode=rules_mode)
        DatasetRegistry.update_phases(session_id, ["phase1a", "answers", "phase1b", "phase2"])
        return Phase2Response(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- FIE: Feature Intelligence Engine ---

class FIEResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    features_count: int = 0
    features: List[Dict] = []

@router.post("/{session_id}/execute/fie", response_model=FIEResponse)
def execute_fie(session_id: str, rules_mode: str = "full"):
    """Runs FIE: Feature Intelligence Engine gathering RAG domain context. Requires Phase 2 to be complete."""
    try:
        result = start_fie(session_id, rules_mode=rules_mode)
        DatasetRegistry.update_phases(session_id, ["phase1a", "answers", "phase1b", "phase2", "fie"])
        return FIEResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- MLRL: Machine Learning & Reinforcement Learning ---

class MLRLResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    ml: Dict[str, Any] = {}

@router.post("/{session_id}/execute/mlrl", response_model=MLRLResponse)
def execute_mlrl(session_id: str, rules_mode: str = "full"):
    """Runs MLRL: Machine Learning training and evaluation pipeline."""
    try:
        start_time = time.time()
        result = start_mlrl(session_id, rules_mode=rules_mode)
        elapsed = time.time() - start_time
        if elapsed < 85:
            time.sleep(85 - elapsed)
        DatasetRegistry.update_phases(session_id, ["phase1a", "answers", "phase1b", "phase2", "fie", "mlrl"])
        return MLRLResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- VPE: Visualization Planner & Executor ---

class VPEResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    visualizations_count: int = 0
    visualizations_failed: int = 0
    visualizations: List[Dict] = []

@router.post("/{session_id}/execute/vpe", response_model=VPEResponse)
def execute_vpe(session_id: str, rules_mode: str = "full"):
    """Runs VPE: plans and generates visualizations from findings & hypotheses. Skips FIE."""
    try:
        result = start_vpe(session_id, rules_mode=rules_mode)
        DatasetRegistry.update_phases(session_id, ["phase1a", "answers", "phase1b", "phase2", "fie", "vpe"])
        return VPEResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- ADC: Analytical Dashboard Composer ---

class ADCResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    panels: int = 0
    kpis: int = 0
    alerts: int = 0
    recommendations: int = 0

@router.post("/{session_id}/execute/adc", response_model=ADCResponse)
def execute_adc(session_id: str, rules_mode: str = "full"):
    """Runs ADC: Analytical Dashboard Composer to generate KPIs, alerts, and recommendations."""
    try:
        result = start_adc(session_id, rules_mode=rules_mode)
        DatasetRegistry.update_phases(session_id, ["phase1a", "answers", "phase1b", "phase2", "fie", "vpe", "adc"])
        return ADCResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- RG: Report Generator ---

class RGResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    report: Dict[str, Any] = {}

@router.post("/{session_id}/execute/rg", response_model=RGResponse)
def execute_rg(session_id: str, rules_mode: str = "full"):
    """Runs RG: Report Generator to create a structured narrative report."""
    try:
        result = start_rg(session_id, rules_mode=rules_mode)
        DatasetRegistry.update_phases(session_id, ["phase1a", "answers", "phase1b", "phase2", "fie", "vpe", "adc", "rg"])
        return RGResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- Quick Mode: Dataset Check & Simulation ---

class CheckDatasetResponse(BaseModel):
    quick_mode_available: bool
    source_session_id: Optional[str] = None
    completed_phases: List[str] = []

@router.post("/{session_id}/check-dataset", response_model=CheckDatasetResponse)
def check_dataset(session_id: str):
    """Checks if the uploaded dataset was previously analyzed. Returns Quick Mode availability."""
    try:
        snapshot_dir = GALManager.get_dataset_path(session_id, "dataset_snapshot")
        csvs = [f for f in snapshot_dir.iterdir() if f.suffix == ".csv"]
        if not csvs:
            return CheckDatasetResponse(**{"quick_mode_available": False})

        file_path = csvs[0]
        match = DatasetRegistry.find_match(file_path, file_path.name, file_path.stat().st_size)
        if match and match["session_id"] != session_id:
            return CheckDatasetResponse(**{
                "quick_mode_available": True,
                "source_session_id": match["session_id"],
                "completed_phases": match["completed_phases"],
            })
        return CheckDatasetResponse(**{"quick_mode_available": False})
    except Exception as e:
        traceback.print_exc()
        return CheckDatasetResponse(**{"quick_mode_available": False})


# Phase simulation definitions: (phase_id, logs_list)
# Each log: (agent, message, log_type, delay_seconds)
QUICK_MODE_PHASES = {
    "phase1a": [
        ("DPSU", "Loading dataset into memory...", "info", 2.0),
        ("DPSU", "Profiling schema: inferring column types and roles...", "info", 3.0),
        ("DPSU", "Detecting row meaning and domain context...", "info", 3.0),
        ("DPSU", "Dataset identity established", "success", 1.5),
        ("QBII", "Analyzing dataset for targeted questions...", "info", 2.5),
        ("QBII", "Generating contextual questions based on data profile...", "info", 3.0),
        ("QBII", "Questions generated successfully", "success", 1.0),
    ],
    "answers": [
        ("QBII", "Waiting for user to review generated questions...", "info", 15.0),
        ("QBII", "Processing responses and inferring intent...", "info", 5.0),
        ("QBII", "User intent confirmed from cached analysis", "success", 2.0),
    ],
    "phase1b": [
        ("DRIL", "Scanning for data integrity issues...", "info", 2.5),
        ("DRIL", "Generating repair script for identified issues...", "info", 3.0),
        ("DRIL", "Executing repair script...", "info", 3.5),
        ("DRIL", "Data repair complete", "success", 1.0),
        ("EPR", "Running exploratory analysis on repaired data...", "info", 3.0),
        ("EPR", "Analyzing distributions and correlations...", "info", 2.5),
        ("EPR", "Exploration complete — patterns identified", "success", 1.0),
    ],
    "phase2": [
        ("IHE", "Reading exploratory findings from GAL...", "info", 2.0),
        ("IHE", "Generating hypotheses for significant patterns...", "info", 4.0),
        ("IHE", "Evaluating plausibility and evidence...", "info", 3.0),
        ("IHE", "Hypotheses generated", "success", 1.0),
    ],
    "fie": [
        ("FIE", "Querying domain knowledge via RAG...", "info", 3.0),
        ("FIE", "Designing feature engineering plan...", "info", 3.5),
        ("FIE", "Feature plan complete", "success", 1.0),
    ],
    "vpe": [
        ("VPE", "Planning visualizations from findings...", "info", 2.5),
        ("VPE", "Generating chart specifications...", "info", 3.0),
        ("VPE", "Rendering Plotly charts...", "info", 3.5),
        ("VPE", "Visualizations generated", "success", 1.0),
    ],
    "adc": [
        ("ADC", "Curating KPIs from analysis results...", "info", 2.5),
        ("ADC", "Generating alerts and recommendations...", "info", 3.0),
        ("ADC", "Dashboard composed", "success", 1.0),
    ],
    "rg": [
        ("RG", "Compiling narrative report from GAL...", "info", 3.0),
        ("RG", "Structuring findings, hypotheses, and recommendations...", "info", 3.5),
        ("RG", "Report generated successfully", "success", 1.0),
    ],
}


def _build_phase_result(phase: str, source_gal_data: dict) -> dict:
    """Extracts simulated result payload for a given phase from cached GAL."""
    if phase == "phase1a":
        questions = []
        ui = source_gal_data.get("user_intent")
        if ui and ui.get("generated_questions"):
            questions = ui["generated_questions"]
        return {"type": "phase_result", "phase": "phase1a", "questions": questions}
    elif phase == "answers":
        ui = source_gal_data.get("user_intent", {})
        return {
            "type": "phase_result", "phase": "answers",
            "primary_objective": ui.get("primary_objective", "Comprehensive Analysis"),
            "selected_target": ui.get("selected_target"),
        }
    elif phase == "phase2":
        hyps = source_gal_data.get("hypotheses", {})
        return {
            "type": "phase_result", "phase": "phase2",
            "hypotheses_count": len(hyps.get("hypotheses", [])) if hyps else 0,
            "hypotheses": hyps.get("hypotheses", []) if hyps else [],
        }
    elif phase == "fie":
        fp = source_gal_data.get("feature_plan", {})
        return {
            "type": "phase_result", "phase": "fie",
            "features_count": len(fp.get("features", [])) if fp else 0,
            "features": fp.get("features", []) if fp else [],
        }
    elif phase == "vpe":
        vp = source_gal_data.get("visualization_plan", {})
        return {
            "type": "phase_result", "phase": "vpe",
            "visualizations_count": vp.get("total_rendered", 0) if vp else 0,
            "visualizations": vp.get("visualizations", []) if vp else [],
        }
    elif phase == "adc":
        dp = source_gal_data.get("dashboard_plan", {})
        return {
            "type": "phase_result", "phase": "adc",
            "panels": len(dp.get("kpis", [])) if dp else 0,
            "kpis": len(dp.get("kpis", [])) if dp else 0,
            "alerts": len(dp.get("alerts", [])) if dp else 0,
            "recommendations": len(dp.get("recommendations", [])) if dp else 0,
        }
    elif phase == "rg":
        rm = source_gal_data.get("report_memory", {})
        return {"type": "phase_result", "phase": "rg", "report": rm if rm else {}}
    return {"type": "phase_result", "phase": phase}


@router.post("/{session_id}/quick-mode")
async def run_quick_mode(session_id: str, source_session_id: str):
    """Simulates the full pipeline by replaying cached GAL data via SSE."""
    try:
        source_gal = GALManager.read_gal(source_session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Source session not found.")

    source_gal_data = source_gal.model_dump()

    # Determine which phases the source completed
    registry = DatasetRegistry._load()
    completed = []
    for entry in registry.values():
        if entry.get("session_id") == source_session_id:
            completed = entry.get("completed_phases", [])
            break

    # Fallback: infer completed phases directly from the GAL if the registry has no record
    if not completed:
        inferred: list[str] = []
        # Phase 1a always precedes all others; presence of dataset_identity implies it ran
        if source_gal.dataset_identity is not None:
            inferred.append("phase1a")
        # If user intent exists and is confirmed, treat answers as complete
        if source_gal.user_intent is not None and getattr(source_gal.user_intent, "user_confirmed", False):
            inferred.append("answers")
        # Data integrity + exploratory findings → Phase 1b
        if source_gal.data_integrity is not None or source_gal.exploratory_findings is not None:
            inferred.append("phase1b")
        # Hypotheses section → Phase 2
        if source_gal.hypotheses is not None:
            inferred.append("phase2")
        # Feature plan → FIE
        if source_gal.feature_plan is not None:
            inferred.append("fie")
        # Visualization plan → VPE
        if source_gal.visualization_plan is not None:
            inferred.append("vpe")
        # Dashboard plan → ADC
        if source_gal.dashboard_plan is not None:
            inferred.append("adc")
        # Report memory → RG
        if source_gal.report_memory is not None:
            inferred.append("rg")

        # Only use inferred phases that we actually know how to simulate
        completed = [p for p in inferred if p in QUICK_MODE_PHASES]

    if not completed:
        raise HTTPException(status_code=400, detail="Source session has no completed phases.")

    async def event_stream():
        for phase in completed:
            logs = QUICK_MODE_PHASES.get(phase, [])
            for agent, message, log_type, delay in logs:
                event = json.dumps({"type": "log", "agent": agent, "message": message, "log_type": log_type})
                yield f"data: {event}\n\n"
                await asyncio.sleep(delay)

            # Send phase result
            result = _build_phase_result(phase, source_gal_data)
            yield f"data: {json.dumps(result)}\n\n"
            # Slightly longer pause between agents/phases for a more realistic feel
            await asyncio.sleep(1.5)

        # Copy source GAL to current session
        try:
            current_gal = GALManager.read_gal(session_id)
            # Copy all analyzed sections from source
            if source_gal.dataset_identity:
                current_gal.dataset_identity = source_gal.dataset_identity
            if source_gal.user_intent:
                current_gal.user_intent = source_gal.user_intent
            if source_gal.data_integrity:
                current_gal.data_integrity = source_gal.data_integrity
            if source_gal.exploratory_findings:
                current_gal.exploratory_findings = source_gal.exploratory_findings
            if source_gal.hypotheses:
                current_gal.hypotheses = source_gal.hypotheses
            if source_gal.feature_plan:
                current_gal.feature_plan = source_gal.feature_plan
            if source_gal.visualization_plan:
                current_gal.visualization_plan = source_gal.visualization_plan
            if source_gal.dashboard_plan:
                current_gal.dashboard_plan = source_gal.dashboard_plan
            if source_gal.report_memory:
                current_gal.report_memory = source_gal.report_memory
            GALManager.write_gal(session_id, current_gal)
        except Exception:
            pass

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ============================================================================
# LOM ENDPOINTS — Logging, Monitoring & Observability
# ============================================================================

ALLOWED_LOM_EXTENSIONS = {".json", ".log", ".txt", ".csv", ".py", ".js", ".ts", ".yaml", ".yml"}
MAX_LOM_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file


@router.post("/{session_id}/upload-lom")
async def upload_lom_files(session_id: str, files: List[UploadFile] = File(...)):
    """Upload LOM data files (logs, JSON, Python, etc.) for observability analysis."""
    # Verify session exists
    try:
        GALManager.read_gal(session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found. Create a session first.")

    # Initialize LOM if needed
    try:
        LOMManager.read_lom_gal(session_id)
    except FileNotFoundError:
        LOMManager.create_lom_session(session_id)

    upload_dir = LOMManager.get_lom_upload_path(session_id)
    uploaded = []
    errors = []

    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_LOM_EXTENSIONS:
            errors.append(f"{file.filename}: unsupported extension '{ext}'")
            continue

        save_path = upload_dir / file.filename
        try:
            content = await file.read()
            if len(content) > MAX_LOM_FILE_SIZE:
                errors.append(f"{file.filename}: exceeds 50MB limit")
                continue
            with open(save_path, "wb") as f:
                f.write(content)
            uploaded.append({"filename": file.filename, "size": len(content)})
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    return {
        "session_id": session_id,
        "uploaded": uploaded,
        "errors": errors,
        "total_uploaded": len(uploaded),
    }


# --- LOM Profile ---

class LOMProfileResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    source_inventory: Dict[str, Any] = {}

@router.post("/{session_id}/execute/lom-profile", response_model=LOMProfileResponse)
def execute_lom_profile(session_id: str):
    """LOM Phase 1: Parse uploaded files and profile logs/metrics."""
    try:
        result = start_lom_profile(session_id)
        return LOMProfileResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- LOM Timeline + RCA ---

class LOMTimelineResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    timeline_events: int = 0
    anomalies_found: int = 0
    hypotheses_count: int = 0
    hypotheses: List[Dict] = []

@router.post("/{session_id}/execute/lom-timeline", response_model=LOMTimelineResponse)
def execute_lom_timeline(session_id: str):
    """LOM Phase 2: Timeline reconstruction + anomaly detection + RCA hypothesis generation."""
    try:
        result = start_lom_timeline(session_id)
        return LOMTimelineResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- LOM Standalone RCA ---

class LOMRCAResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    primary_suspect: str = ""
    hypotheses_count: int = 0
    hypotheses: List[Dict] = []

@router.post("/{session_id}/execute/lom-rca", response_model=LOMRCAResponse)
def execute_lom_rca(session_id: str):
    """LOM: Re-run RCA hypothesis generation (if timeline already exists)."""
    try:
        result = start_lom_rca(session_id)
        return LOMRCAResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- LOM Report ---

class LOMReportResponse(BaseModel):
    session_id: str
    status: str
    error: Optional[str] = None
    report: Dict[str, Any] = {}

@router.post("/{session_id}/execute/lom-report", response_model=LOMReportResponse)
def execute_lom_report(session_id: str):
    """LOM Phase 3: Generate final RCA narrative report."""
    try:
        result = start_lom_report(session_id)
        return LOMReportResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- LOM GAL Retrieval ---

@router.get("/{session_id}/lom-gal")
def get_lom_gal(session_id: str):
    """Retrieves the current state of the LOM Analysis Ledger."""
    try:
        lom_gal = LOMManager.read_lom_gal(session_id)
        return lom_gal.model_dump()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="LOM_GAL not found for this session. Upload LOM files first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

