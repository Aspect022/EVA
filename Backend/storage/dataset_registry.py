import hashlib
import json
from pathlib import Path
from typing import Optional, List

REGISTRY_PATH = Path("eva_sessions") / "_dataset_registry.json"


class DatasetRegistry:
    """Tracks previously analyzed datasets by SHA-256 hash for Quick Mode replay."""

    @staticmethod
    def _load() -> dict:
        if REGISTRY_PATH.exists():
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def _save(registry: dict):
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

    @staticmethod
    def compute_hash(file_path: Path) -> str:
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()

    @classmethod
    def register(cls, file_path: Path, filename: str, size_bytes: int, session_id: str, completed_phases: List[str]):
        registry = cls._load()
        file_hash = cls.compute_hash(file_path)
        registry[file_hash] = {
            "filename": filename,
            "size_bytes": size_bytes,
            "session_id": session_id,
            "completed_phases": completed_phases,
        }
        cls._save(registry)

    @classmethod
    def find_match(cls, file_path: Path, filename: str, size_bytes: int) -> Optional[dict]:
        registry = cls._load()
        file_hash = cls.compute_hash(file_path)
        entry = registry.get(file_hash)
        if entry and entry.get("completed_phases"):
            return entry
        return None

    @classmethod
    def update_phases(cls, session_id: str, completed_phases: List[str]):
        registry = cls._load()
        for file_hash, entry in registry.items():
            if entry.get("session_id") == session_id:
                entry["completed_phases"] = completed_phases
                cls._save(registry)
                return
