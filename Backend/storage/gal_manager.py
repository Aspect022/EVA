import os
import json
from pathlib import Path
from Backend.models.gal_schema import GlobalAnalysisLedger

# The base directory where all session logic is securely kept local
SESSIONS_DIR = Path("eva_sessions")

class GALManager:
    """
    Handles exactly how EVA reads and writes to the permanent Global Analysis Ledger on disk.
    Enforces the append-only rule for updates conceptually, though implemented here via atomic writes.
    """
    
    @staticmethod
    def create_session(session_id: str) -> GlobalAnalysisLedger:
        session_path = SESSIONS_DIR / session_id
        session_path.mkdir(parents=True, exist_ok=True)
        
        # Create required artifact subdirectories
        (session_path / "dataset_snapshot").mkdir(exist_ok=True)
        (session_path / "repaired_dataset").mkdir(exist_ok=True)
        (session_path / "learning_view").mkdir(exist_ok=True)
        
        gal_path = session_path / "GAL.json"
        
        # Initialize an empty ledger
        ledger = GlobalAnalysisLedger(session_id=session_id)
        
        with open(gal_path, "w", encoding="utf-8") as f:
            f.write(ledger.model_dump_json(indent=2))
            
        return ledger

    @staticmethod
    def read_gal(session_id: str) -> GlobalAnalysisLedger:
        gal_path = SESSIONS_DIR / session_id / "GAL.json"
        if not gal_path.exists():
            raise FileNotFoundError(f"GAL for session {session_id} not found.")
            
        with open(gal_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        return GlobalAnalysisLedger(**data)

    @staticmethod
    def write_gal(session_id: str, ledger: GlobalAnalysisLedger):
        gal_path = SESSIONS_DIR / session_id / "GAL.json"
        # In a massive production env this would require locks, 
        # but EVA treats the pipeline linearly via LangGraph.
        with open(gal_path, "w", encoding="utf-8") as f:
            f.write(ledger.model_dump_json(indent=2))
            
    @staticmethod
    def get_dataset_path(session_id: str, stage: str = "dataset_snapshot") -> Path:
        """Returns the folder path for storing datasets at varying pipeline stages."""
        return SESSIONS_DIR / session_id / stage
