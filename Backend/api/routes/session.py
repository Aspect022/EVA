import uuid
import shutil
import os
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from Backend.storage.gal_manager import GALManager
from Backend.orchestrator.pipeline import start_phase_1, start_phase_1a, start_phase_1b, submit_user_answers, start_phase_2, start_fie, start_vpe, start_adc

import traceback
from typing import Optional, Dict, List

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
    has_visualizations: bool = False
    has_dashboard: bool = False
    csv_file: Optional[str] = None

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
            results.append(SessionInfo(
                session_id=entry.name,
                has_identity=gal.dataset_identity is not None,
                has_intent=gal.user_intent is not None and gal.user_intent.user_confirmed,
                has_visualizations=gal.visualization_plan is not None,
                has_features=gal.feature_plan is not None,
                has_integrity=gal.data_integrity is not None,
                has_findings=gal.exploratory_findings is not None,
                has_hypotheses=gal.hypotheses is not None,
                has_dashboard=gal.dashboard_plan is not None,
                csv_file=csv_file,
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
        return FIEResponse(**result)
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
        return ADCResponse(**result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

