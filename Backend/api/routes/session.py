import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from Backend.storage.gal_manager import GALManager
from Backend.orchestrator.pipeline import start_phase_1

router = APIRouter()

class SessionResponse(BaseModel):
    session_id: str
    message: str

@router.post("/create", response_model=SessionResponse)
def create_session():
    """Step 0: Initialize empty analysis universe."""
    session_id = str(uuid.uuid4())
    try:
        # Spin up new GAL identity
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
        # Enforce folder exists
        gal = GALManager.read_gal(session_id) 
        
        # Save snapshot
        snapshot_dir = GALManager.get_dataset_path(session_id, "dataset_snapshot")
        save_path = snapshot_dir / file.filename
        
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"filename": file.filename, "status": "uploaded", "session_id": session_id}
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ExecuteResponse(BaseModel):
    session_id: str
    status: str
    error: str = None

@router.post("/{session_id}/execute")
def execute_pipeline(session_id: str, csv_file_name: str):
    """Triggers the LangGraph pipeline execution for Phase 1."""
    try:
        # For phase 1, blocks HTTP until completion
        result = start_phase_1(session_id, csv_file_name)
        return ExecuteResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/gal")
def get_gal(session_id: str):
    """Retrieves the current state of the Global Analysis Ledger."""
    try:
        gal = GALManager.read_gal(session_id)
        return gal.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
