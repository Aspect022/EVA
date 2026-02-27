"""
Integration test for the LOM pipeline.
Tests the parser, schema, and storage layers without requiring LLM calls.
Run from project root: python scripts/test_lom_pipeline.py
"""
import sys
import os
import json
import shutil
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from Backend.models.lom_schema import (
    LOMAnalysisLedger, SourceInventory, LogProfile, MetricProfile,
    CodeContext, TimelineReconstruction, AnomalyFindings,
    RCAHypotheses, RCAReport, ParsedLogEntry, MetricDataPoint, CodeArtifact,
)
from Backend.agents.lom_parser import LOMParser, LOMDocument
from Backend.storage.gal_manager import GALManager, LOMManager


SAMPLE_DATA_DIR = Path(__file__).parent / "sample_lom_data"
TEST_SESSION_ID = "test-lom-integration-001"
SESSIONS_DIR = PROJECT_ROOT / "eva_sessions"


def test_schema_creation():
    """Test LOM schema Pydantic models can be instantiated."""
    print("--- Test: Schema Creation ---")

    ledger = LOMAnalysisLedger(session_id="test-123")
    assert ledger.session_id == "test-123"
    assert ledger.analysis_type == "RCA"
    assert ledger.source_inventory is None
    assert ledger.rca_report is None

    # Test nested models
    inventory = SourceInventory(total_files=3, total_log_entries=100)
    assert inventory.total_files == 3

    profile = LogProfile(total_entries=50, error_rate_percent=12.5)
    assert profile.error_rate_percent == 12.5

    report = RCAReport(executive_summary="Test summary", confidence_level="High")
    assert report.confidence_level == "High"

    print("  ✅ All schema models instantiate correctly")


def test_parser_json():
    """Test JSON file parsing."""
    print("--- Test: JSON Parser ---")

    json_path = SAMPLE_DATA_DIR / "sample_kibana_export.json"
    assert json_path.exists(), f"Sample JSON not found: {json_path}"

    doc = LOMParser.parse_single_file(json_path)

    assert len(doc.source_files) == 1
    sf = doc.source_files[0]
    assert sf.filename == "sample_kibana_export.json"
    assert sf.file_type == "json"
    assert sf.parse_status == "success"

    assert len(doc.log_entries) > 0
    print(f"  Parsed {len(doc.log_entries)} log entries from JSON")

    # Check that error entries are captured
    errors = [e for e in doc.log_entries if e.level in ("ERROR", "FATAL")]
    assert len(errors) > 0, "Should have parsed ERROR/FATAL entries"
    print(f"  Found {len(errors)} ERROR/FATAL entries")

    print("  ✅ JSON parser works correctly")


def test_parser_log():
    """Test plain log file parsing."""
    print("--- Test: Log File Parser ---")

    log_path = SAMPLE_DATA_DIR / "sample_app.log"
    assert log_path.exists(), f"Sample log not found: {log_path}"

    doc = LOMParser.parse_single_file(log_path)

    assert len(doc.source_files) == 1
    sf = doc.source_files[0]
    assert sf.file_type == "log"
    assert sf.parse_status == "success"

    assert len(doc.log_entries) > 0
    print(f"  Parsed {len(doc.log_entries)} log entries from log file")

    # Check timestamp extraction
    entries_with_timestamps = [e for e in doc.log_entries if e.timestamp]
    assert len(entries_with_timestamps) > 0, "Should have extracted timestamps"
    print(f"  {len(entries_with_timestamps)} entries have timestamps")

    # Check level detection
    errors = [e for e in doc.log_entries if e.level in ("ERROR", "FATAL")]
    warns = [e for e in doc.log_entries if e.level in ("WARN", "WARNING")]
    print(f"  Levels: {len(errors)} errors, {len(warns)} warnings")

    print("  ✅ Log parser works correctly")


def test_parser_python():
    """Test Python code file parsing."""
    print("--- Test: Python Code Parser ---")

    py_path = SAMPLE_DATA_DIR / "sample_traceback.py"
    assert py_path.exists(), f"Sample Python not found: {py_path}"

    doc = LOMParser.parse_single_file(py_path)

    assert len(doc.code_artifacts) == 1
    artifact = doc.code_artifacts[0]
    assert artifact.language == "python"
    assert artifact.filename == "sample_traceback.py"

    # Should detect functions
    assert len(artifact.functions_detected) > 0
    print(f"  Functions detected: {artifact.functions_detected}")

    # Should detect error type from traceback
    if artifact.error_type:
        print(f"  Error type: {artifact.error_type}")
    if artifact.traceback:
        print(f"  Traceback found ({len(artifact.traceback)} chars)")

    print("  ✅ Python parser works correctly")


def test_parser_directory():
    """Test parsing entire directory of sample files."""
    print("--- Test: Directory Parser ---")

    doc = LOMParser.parse_directory(SAMPLE_DATA_DIR)

    assert len(doc.source_files) >= 3, f"Expected at least 3 source files, got {len(doc.source_files)}"
    print(f"  Total source files: {len(doc.source_files)}")
    print(f"  Total log entries: {len(doc.log_entries)}")
    print(f"  Total metric points: {len(doc.metric_points)}")
    print(f"  Total code artifacts: {len(doc.code_artifacts)}")

    # Test source inventory builder
    inventory = LOMParser.build_source_inventory(doc)
    assert inventory["total_files"] >= 3
    print(f"  Source inventory: {json.dumps(inventory, indent=2, default=str)}")

    # Test LLM summary builder
    summary = LOMParser.build_llm_summary(doc)
    assert len(summary) > 100, "LLM summary should be substantial"
    print(f"  LLM summary length: {len(summary)} chars")

    print("  ✅ Directory parser works correctly")


def test_lom_session_lifecycle():
    """Test LOM session creation, read, write cycle."""
    print("--- Test: LOM Session Lifecycle ---")

    session_dir = SESSIONS_DIR / TEST_SESSION_ID
    try:
        # Clean up from previous runs
        if session_dir.exists():
            shutil.rmtree(session_dir)

        # Create the base session first (needed for LOM)
        GALManager.create_session(TEST_SESSION_ID)
        print("  Created base session")

        # Create LOM session
        ledger = LOMManager.create_lom_session(TEST_SESSION_ID)
        assert ledger.session_id == TEST_SESSION_ID
        assert (session_dir / "LOM_GAL.json").exists()
        assert (session_dir / "lom_uploads").is_dir()
        print("  Created LOM session with LOM_GAL.json and lom_uploads/")

        # Read it back
        ledger = LOMManager.read_lom_gal(TEST_SESSION_ID)
        assert ledger.session_id == TEST_SESSION_ID
        print("  Read LOM_GAL.json successfully")

        # Write a section
        ledger.source_inventory = SourceInventory(total_files=5, total_log_entries=200)
        LOMManager.write_lom_gal(TEST_SESSION_ID, ledger)
        print("  Wrote source_inventory to LOM_GAL.json")

        # Read and verify
        ledger2 = LOMManager.read_lom_gal(TEST_SESSION_ID)
        assert ledger2.source_inventory is not None
        assert ledger2.source_inventory.total_files == 5
        print("  Verified source_inventory persisted correctly")

        # Verify GAL.json is untouched
        gal = GALManager.read_gal(TEST_SESSION_ID)
        assert gal.dataset_identity is None, "GAL.json should be untouched by LOM operations"
        print("  ✅ GAL.json is completely untouched (isolation confirmed)")

        print("  ✅ LOM session lifecycle works correctly")

    finally:
        # Cleanup
        if session_dir.exists():
            shutil.rmtree(session_dir)
            print("  Cleaned up test session directory")


def test_full_parse_and_store():
    """Test: parse sample data → build inventory → store in LOM_GAL."""
    print("--- Test: Full Parse + Store ---")

    session_dir = SESSIONS_DIR / TEST_SESSION_ID
    try:
        if session_dir.exists():
            shutil.rmtree(session_dir)

        GALManager.create_session(TEST_SESSION_ID)
        ledger = LOMManager.create_lom_session(TEST_SESSION_ID)

        # Copy sample files to upload dir
        upload_dir = LOMManager.get_lom_upload_path(TEST_SESSION_ID)
        for f in SAMPLE_DATA_DIR.iterdir():
            if f.is_file():
                shutil.copy2(f, upload_dir / f.name)
        print(f"  Copied sample files to {upload_dir}")

        # Parse directory
        doc = LOMParser.parse_directory(upload_dir)
        print(f"  Parsed: {len(doc.log_entries)} logs, {len(doc.metric_points)} metrics, "
              f"{len(doc.code_artifacts)} code")

        # Build and store source inventory
        inventory_data = LOMParser.build_source_inventory(doc)
        ledger.source_inventory = SourceInventory(**inventory_data)

        # Store code context
        if doc.code_artifacts:
            ledger.code_context = CodeContext(artifacts=doc.code_artifacts)

        LOMManager.write_lom_gal(TEST_SESSION_ID, ledger)

        # Verify stored state
        ledger = LOMManager.read_lom_gal(TEST_SESSION_ID)
        assert ledger.source_inventory is not None
        assert ledger.source_inventory.total_files >= 3
        if ledger.code_context:
            assert len(ledger.code_context.artifacts) > 0
            print(f"  Stored code context: {len(ledger.code_context.artifacts)} artifacts")

        # Verify isolation
        gal = GALManager.read_gal(TEST_SESSION_ID)
        assert gal.dataset_identity is None

        print("  ✅ Full parse + store pipeline works correctly")
        print("  ✅ CSV pipeline isolation confirmed")

    finally:
        if session_dir.exists():
            shutil.rmtree(session_dir)


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print(" LOM Pipeline Integration Tests")
    print("=" * 60 + "\n")

    tests = [
        test_schema_creation,
        test_parser_json,
        test_parser_log,
        test_parser_python,
        test_parser_directory,
        test_lom_session_lifecycle,
        test_full_parse_and_store,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  ❌ FAILED: {e}")
            import traceback as tb
            tb.print_exc()
        print()

    print("=" * 60)
    print(f" Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
