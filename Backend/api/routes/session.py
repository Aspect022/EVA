import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from Backend.storage.gal_manager import GALManager
from Backend.orchestrator.pipeline import start_phase_1, start_phase_1a, start_phase_1b, submit_user_answers

import traceback
from typing import Optional, Dict, List

router = APIRouter()

class SessionResponse(BaseModel):
    session_id: str
    message: str

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
def execute_phase_1a(session_id: str, csv_file_name: str):
    """Runs DPSU + QBII question generation. Returns questions for the user."""
    try:
        result = start_phase_1a(session_id, csv_file_name)
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
    analytical_goal: Optional[str] = None
    selected_target: Optional[str] = None

@router.post("/{session_id}/submit-answers", response_model=IntentResponse)
def submit_answers(session_id: str, body: UserAnswersRequest):
    """Submit user answers to QBII questions. Infers and confirms intent."""
    try:
        result = submit_user_answers(session_id, body.answers)
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
def execute_phase_1b(session_id: str, csv_file_name: str):
    """Runs DRIL + EPR after user intent is confirmed."""
    try:
        result = start_phase_1b(session_id, csv_file_name)
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
