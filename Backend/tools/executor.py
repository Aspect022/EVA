"""
Code Executor — Local Script Runner for EVA Agents.

Agents generate Python scripts. This module saves, executes, and captures
results from those scripts in an isolated subprocess, keeping the main
process safe from side-effects.
"""
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from Backend.storage.gal_manager import GALManager


@dataclass
class ExecutionResult:
    """Captures every observable outcome of a script run."""
    script_path: str
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    output_files: list[str] = field(default_factory=list)


class CodeExecutor:
    """
    Saves a Python script to the session's scripts/ directory and runs it
    using the active Python interpreter via subprocess.

    The generated script receives two environment variables:
      - EVA_INPUT_PATH  : absolute path to the CSV the script should read
      - EVA_OUTPUT_PATH : absolute path where the script must write results
    """

    @staticmethod
    def execute(
        session_id: str,
        script_content: str,
        input_csv_path: str,
        output_csv_path: str,
        script_name: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> ExecutionResult:
        from Backend.config import settings
        if timeout_seconds is None:
            timeout_seconds = settings.execution.default_timeout
        # Resolve ALL paths to absolute to avoid cwd-relative doubling
        scripts_dir = GALManager.get_dataset_path(session_id, "scripts").resolve()
        scripts_dir.mkdir(parents=True, exist_ok=True)

        input_abs = Path(input_csv_path).resolve()
        output_abs = Path(output_csv_path).resolve()

        # Ensure output directory exists
        output_abs.parent.mkdir(parents=True, exist_ok=True)

        # Deterministic or auto-generated filename
        if not script_name:
            script_name = f"script_{uuid.uuid4().hex[:8]}.py"
        script_path = scripts_dir / script_name

        # Write the generated code to disk for full traceability
        script_path.write_text(script_content, encoding="utf-8")

        # Set cwd to the project root so relative imports in scripts work
        project_root = Path(__file__).resolve().parent.parent.parent

        # Build environment with absolute paths
        env = {
            **os.environ,
            "EVA_INPUT_PATH": str(input_abs),
            "EVA_OUTPUT_PATH": str(output_abs),
            "PYTHONIOENCODING": "utf-8",
        }

        try:
            result = subprocess.run(
                [sys.executable, str(script_path.resolve())],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=env,
                cwd=str(project_root),
            )

            # Check what output files the script produced
            output_files = []
            if output_abs.exists():
                output_files.append(str(output_abs))

            return ExecutionResult(
                script_path=str(script_path),
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                success=result.returncode == 0,
                output_files=output_files,
            )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                script_path=str(script_path),
                exit_code=-1,
                stdout="",
                stderr=f"Script timed out after {timeout_seconds}s",
                success=False,
            )
        except Exception as e:
            return ExecutionResult(
                script_path=str(script_path),
                exit_code=-1,
                stdout="",
                stderr=str(e),
                success=False,
            )
