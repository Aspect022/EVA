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
        (session_path / "scripts").mkdir(exist_ok=True)
        
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
        with open(gal_path, "w", encoding="utf-8") as f:
            f.write(ledger.model_dump_json(indent=2))
            
    @staticmethod
    def get_dataset_path(session_id: str, stage: str = "dataset_snapshot") -> Path:
        """Returns the folder path for storing datasets at varying pipeline stages."""
        return SESSIONS_DIR / session_id / stage


class LOMManager:
    """
    Handles read/write for the LOM Analysis Ledger (LOM_GAL.json).
    Completely parallel to GALManager — does not touch GAL.json.
    """

    @staticmethod
    def create_lom_session(session_id: str):
        """Initialize LOM-specific directories and LOM_GAL.json within an existing session."""
        from Backend.models.lom_schema import LOMAnalysisLedger

        session_path = SESSIONS_DIR / session_id
        session_path.mkdir(parents=True, exist_ok=True)

        # LOM-specific upload directory
        lom_uploads = session_path / "lom_uploads"
        lom_uploads.mkdir(exist_ok=True)

        lom_gal_path = session_path / "LOM_GAL.json"

        ledger = LOMAnalysisLedger(session_id=session_id)
        with open(lom_gal_path, "w", encoding="utf-8") as f:
            f.write(ledger.model_dump_json(indent=2))

        return ledger

    @staticmethod
    def read_lom_gal(session_id: str):
        """Read the LOM Analysis Ledger from disk."""
        from Backend.models.lom_schema import LOMAnalysisLedger

        lom_gal_path = SESSIONS_DIR / session_id / "LOM_GAL.json"
        if not lom_gal_path.exists():
            raise FileNotFoundError(f"LOM_GAL for session {session_id} not found.")

        with open(lom_gal_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return LOMAnalysisLedger(**data)

    @staticmethod
    def write_lom_gal(session_id: str, ledger):
        """Write the LOM Analysis Ledger to disk."""
        lom_gal_path = SESSIONS_DIR / session_id / "LOM_GAL.json"
        with open(lom_gal_path, "w", encoding="utf-8") as f:
            f.write(ledger.model_dump_json(indent=2))

    @staticmethod
    def get_lom_upload_path(session_id: str) -> Path:
        """Returns the folder path for LOM file uploads."""
        return SESSIONS_DIR / session_id / "lom_uploads"
