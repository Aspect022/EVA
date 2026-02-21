import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from Backend.storage.gal_manager import GALManager

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
