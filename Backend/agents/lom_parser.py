"""
Universal LOM Data Parser
Accepts uploaded files of various formats and normalizes them into structured
LOMDocument objects for downstream analysis by LOM agents.
"""
import os
import re
import json
import csv
import io
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from Backend.models.lom_schema import (
    ParsedLogEntry, MetricDataPoint, CodeArtifact, LOMSourceFile,
)


# --- Supported extensions and their parser strategies ---
EXTENSION_MAP = {
    ".json": "json",
    ".log": "log",
    ".txt": "log",
    ".csv": "metric_csv",
    ".py": "code",
    ".js": "code",
    ".ts": "code",
    ".yaml": "config",
    ".yml": "config",
}

# Common log timestamp patterns (ISO 8601, syslog, common log format)
TIMESTAMP_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?",
    r"\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}",
    r"\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}",
    r"\d{10,13}",  # Unix epoch in seconds or milliseconds
]

LOG_LEVEL_PATTERN = re.compile(
    r"\b(DEBUG|INFO|WARN(?:ING)?|ERROR|FATAL|CRITICAL|TRACE|NOTICE|SEVERE)\b",
    re.IGNORECASE,
)

# Max lines to send to LLM for any single source
MAX_PREVIEW_LINES = 200
MAX_LOG_ENTRIES = 5000


@dataclass
class LOMDocument:
    """Unified container for all parsed LOM data from multiple uploaded files."""
    log_entries: List[ParsedLogEntry] = field(default_factory=list)
    metric_points: List[MetricDataPoint] = field(default_factory=list)
    code_artifacts: List[CodeArtifact] = field(default_factory=list)
    config_artifacts: List[CodeArtifact] = field(default_factory=list)
    source_files: List[LOMSourceFile] = field(default_factory=list)
    raw_json_objects: List[Dict[str, Any]] = field(default_factory=list)


class LOMParser:
    """Parses various file formats into a unified LOMDocument."""

    @staticmethod
    def parse_directory(upload_dir: Path) -> LOMDocument:
        """Parse all files in the upload directory into a single LOMDocument."""
        doc = LOMDocument()
        if not upload_dir.exists():
            return doc

        for file_path in sorted(upload_dir.iterdir()):
            if file_path.is_file() and not file_path.name.startswith("."):
                LOMParser._parse_file(file_path, doc)

        return doc

    @staticmethod
    def parse_single_file(file_path: Path) -> LOMDocument:
        """Parse a single file into a LOMDocument."""
        doc = LOMDocument()
        LOMParser._parse_file(file_path, doc)
        return doc

    @staticmethod
    def _parse_file(file_path: Path, doc: LOMDocument):
        """Route a file to the appropriate parser based on extension."""
        ext = file_path.suffix.lower()
        strategy = EXTENSION_MAP.get(ext, "log")  # Default to log parser for unknown

        source_meta = LOMSourceFile(
            filename=file_path.name,
            file_type=strategy,
            size_bytes=file_path.stat().st_size,
        )

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            source_meta.line_count = len(lines)

            if strategy == "json":
                entries = LOMParser._parse_json(content, file_path.name, doc)
                source_meta.entries_extracted = entries
            elif strategy == "log":
                entries = LOMParser._parse_log(lines, file_path.name, doc)
                source_meta.entries_extracted = entries
            elif strategy == "metric_csv":
                entries = LOMParser._parse_metric_csv(content, file_path.name, doc)
                source_meta.entries_extracted = entries
            elif strategy == "code":
                LOMParser._parse_code(content, file_path.name, ext, doc)
                source_meta.entries_extracted = 1
            elif strategy == "config":
                LOMParser._parse_config(content, file_path.name, doc)
                source_meta.entries_extracted = 1

            source_meta.parse_status = "success"

            # Detect time range
            time_range = LOMParser._detect_time_range(doc, strategy)
            if time_range:
                source_meta.time_range_start, source_meta.time_range_end = time_range

        except Exception as e:
            source_meta.parse_status = "failed"
            source_meta.parse_notes = str(e)

        doc.source_files.append(source_meta)

    # --- JSON Parser ---

    @staticmethod
    def _parse_json(content: str, filename: str, doc: LOMDocument) -> int:
        """Parse JSON files — handles Kibana/Grafana exports, structured logs, nested objects."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try line-delimited JSON (NDJSON)
            entries = 0
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    entries += LOMParser._process_json_object(obj, filename, doc)
                except json.JSONDecodeError:
                    continue
            return entries

        if isinstance(data, list):
            total = 0
            for item in data[:MAX_LOG_ENTRIES]:
                total += LOMParser._process_json_object(item, filename, doc)
            return total
        elif isinstance(data, dict):
            # Kibana/ES export format: look for "hits.hits" or "responses"
            hits = LOMParser._extract_nested_hits(data)
            if hits:
                total = 0
                for hit in hits[:MAX_LOG_ENTRIES]:
                    total += LOMParser._process_json_object(hit, filename, doc)
                return total
            return LOMParser._process_json_object(data, filename, doc)

        return 0

    @staticmethod
    def _extract_nested_hits(data: dict) -> Optional[List[dict]]:
        """Extract log entries from common export formats (Elasticsearch, Kibana, Grafana)."""
        # Elasticsearch: hits.hits[]._source
        if "hits" in data and isinstance(data["hits"], dict):
            inner_hits = data["hits"].get("hits", [])
            if inner_hits:
                return [h.get("_source", h) for h in inner_hits if isinstance(h, dict)]

        # Grafana JSON export: results[].frames[].data
        if "results" in data and isinstance(data["results"], dict):
            for key, result in data["results"].items():
                if isinstance(result, dict) and "frames" in result:
                    entries = []
                    for frame in result["frames"]:
                        if "data" in frame and "values" in frame["data"]:
                            entries.append(frame["data"])
                    if entries:
                        return entries

        # Generic: look for any array field with > 5 items
        for key, val in data.items():
            if isinstance(val, list) and len(val) > 5 and all(isinstance(i, dict) for i in val[:5]):
                return val

        return None

    @staticmethod
    def _process_json_object(obj: dict, filename: str, doc: LOMDocument) -> int:
        """Classify a JSON object as a log entry or metric and add to doc."""
        if not isinstance(obj, dict):
            return 0

        doc.raw_json_objects.append(obj)

        # Detect if this looks like a log entry
        log_keys = {"message", "msg", "log", "event", "text", "body"}
        level_keys = {"level", "severity", "log_level", "loglevel", "status"}
        ts_keys = {"timestamp", "@timestamp", "time", "ts", "datetime", "date", "created_at"}

        obj_keys_lower = {k.lower() for k in obj.keys()}

        is_log = bool(obj_keys_lower & log_keys)
        has_level = bool(obj_keys_lower & level_keys)

        if is_log or has_level:
            entry = ParsedLogEntry(
                source=filename,
                metadata=obj,
            )
            # Extract message
            for k in log_keys:
                for orig_k in obj:
                    if orig_k.lower() == k and isinstance(obj[orig_k], str):
                        entry.message = obj[orig_k]
                        break
                if entry.message:
                    break

            # Extract level
            for k in level_keys:
                for orig_k in obj:
                    if orig_k.lower() == k:
                        entry.level = str(obj[orig_k]).upper()
                        break
                if entry.level != "INFO":
                    break

            # Extract timestamp
            for k in ts_keys:
                for orig_k in obj:
                    if orig_k.lower() == k:
                        entry.timestamp = str(obj[orig_k])
                        break
                if entry.timestamp:
                    break

            doc.log_entries.append(entry)
            return 1

        # Detect if this looks like a metric
        metric_keys = {"value", "metric", "gauge", "counter", "count"}
        if obj_keys_lower & metric_keys:
            point = MetricDataPoint(
                metric_name=obj.get("metric", obj.get("name", filename)),
                value=float(obj.get("value", obj.get("gauge", obj.get("count", 0)))),
                labels={k: str(v) for k, v in obj.items() if isinstance(v, (str, int, float)) and k not in ("value", "gauge", "count", "metric")},
            )
            for k in ts_keys:
                for orig_k in obj:
                    if orig_k.lower() == k:
                        point.timestamp = str(obj[orig_k])
                        break
                if point.timestamp:
                    break
            doc.metric_points.append(point)
            return 1

        # Generic JSON — store as raw for LLM inspection
        return 0

    # --- Log File Parser ---

    @staticmethod
    def _parse_log(lines: List[str], filename: str, doc: LOMDocument) -> int:
        """Parse plaintext log files using heuristic timestamp/level detection."""
        entries = 0
        ts_regex = re.compile("|".join(f"({p})" for p in TIMESTAMP_PATTERNS))

        for i, line in enumerate(lines[:MAX_LOG_ENTRIES]):
            line = line.strip()
            if not line:
                continue

            entry = ParsedLogEntry(
                source=filename,
                raw_line=line,
                line_number=i + 1,
                message=line,
            )

            # Extract timestamp
            ts_match = ts_regex.search(line)
            if ts_match:
                entry.timestamp = ts_match.group(0)
                # Remove timestamp from message for cleaner text
                entry.message = line[ts_match.end():].strip()

            # Extract log level
            level_match = LOG_LEVEL_PATTERN.search(line)
            if level_match:
                raw_level = level_match.group(1).upper()
                if raw_level == "WARNING":
                    raw_level = "WARN"
                entry.level = raw_level

            doc.log_entries.append(entry)
            entries += 1

        return entries

    # --- Metric CSV Parser ---

    @staticmethod
    def _parse_metric_csv(content: str, filename: str, doc: LOMDocument) -> int:
        """Parse CSV files as time-series metric data."""
        reader = csv.DictReader(io.StringIO(content))
        entries = 0

        ts_columns = {"timestamp", "time", "datetime", "date", "ts", "@timestamp"}

        for row in reader:
            if entries >= MAX_LOG_ENTRIES:
                break

            row_lower = {k.lower(): k for k in row.keys()}
            ts_value = None
            for ts_col in ts_columns:
                if ts_col in row_lower:
                    ts_value = row[row_lower[ts_col]]
                    break

            # Each numeric column becomes a metric data point
            for col, val in row.items():
                if col.lower() in ts_columns:
                    continue
                try:
                    numeric_val = float(val)
                    point = MetricDataPoint(
                        timestamp=ts_value,
                        metric_name=col,
                        value=numeric_val,
                    )
                    doc.metric_points.append(point)
                    entries += 1
                except (ValueError, TypeError):
                    # Non-numeric column — treat as log entry if it has content
                    if val and len(val) > 10:
                        entry = ParsedLogEntry(
                            source=filename,
                            timestamp=ts_value,
                            message=f"{col}: {val}",
                        )
                        doc.log_entries.append(entry)

        return entries

    # --- Code Parser ---

    @staticmethod
    def _parse_code(content: str, filename: str, ext: str, doc: LOMDocument):
        """Parse code files — extract function signatures, tracebacks, and errors."""
        lang_map = {".py": "python", ".js": "javascript", ".ts": "typescript"}
        language = lang_map.get(ext, "unknown")

        lines = content.splitlines()
        preview = "\n".join(lines[:MAX_PREVIEW_LINES])

        artifact = CodeArtifact(
            filename=filename,
            language=language,
            content_preview=preview,
        )

        # Extract Python traceback
        if language == "python":
            traceback = LOMParser._extract_python_traceback(content)
            if traceback:
                artifact.traceback = traceback

            # Extract error type from traceback
            error_match = re.search(r"(\w+Error|\w+Exception):\s*(.*)", content)
            if error_match:
                artifact.error_type = error_match.group(1)
                artifact.error_message = error_match.group(2).strip()

            # Extract function names
            func_matches = re.findall(r"^(?:def|class)\s+(\w+)", content, re.MULTILINE)
            artifact.functions_detected = func_matches[:50]

        # Extract JS/TS error patterns
        elif language in ("javascript", "typescript"):
            error_match = re.search(r"(TypeError|ReferenceError|SyntaxError|Error):\s*(.*)", content)
            if error_match:
                artifact.error_type = error_match.group(1)
                artifact.error_message = error_match.group(2).strip()

            func_matches = re.findall(r"(?:function|const|let|var)\s+(\w+)\s*(?:=\s*(?:async\s+)?(?:\(|function)|\()", content)
            artifact.functions_detected = func_matches[:50]

        doc.code_artifacts.append(artifact)

    @staticmethod
    def _extract_python_traceback(content: str) -> Optional[str]:
        """Extract the most recent Python traceback from content."""
        tb_pattern = re.compile(
            r"Traceback \(most recent call last\):.*?(?:\w+Error|\w+Exception):.*",
            re.DOTALL,
        )
        matches = list(tb_pattern.finditer(content))
        if matches:
            return matches[-1].group(0)[:2000]  # Cap at 2000 chars
        return None

    # --- Config Parser (YAML) ---

    @staticmethod
    def _parse_config(content: str, filename: str, doc: LOMDocument):
        """Parse YAML/config files as code artifacts with config type."""
        lines = content.splitlines()
        preview = "\n".join(lines[:MAX_PREVIEW_LINES])

        artifact = CodeArtifact(
            filename=filename,
            language="yaml",
            content_preview=preview,
        )
        doc.config_artifacts.append(artifact)

    # --- Utility ---

    @staticmethod
    def _detect_time_range(doc: LOMDocument, strategy: str) -> Optional[Tuple[str, str]]:
        """Try to detect the time range from parsed entries."""
        timestamps = []
        for entry in doc.log_entries:
            if entry.timestamp:
                timestamps.append(entry.timestamp)
        for point in doc.metric_points:
            if point.timestamp:
                timestamps.append(point.timestamp)

        if timestamps:
            timestamps.sort()
            return timestamps[0], timestamps[-1]
        return None

    @staticmethod
    def build_source_inventory(doc: LOMDocument) -> dict:
        """Build a summary suitable for the SourceInventory schema."""
        ts_all = []
        for e in doc.log_entries:
            if e.timestamp:
                ts_all.append(e.timestamp)
        for p in doc.metric_points:
            if p.timestamp:
                ts_all.append(p.timestamp)
        ts_all.sort()

        return {
            "sources": [sf.model_dump() for sf in doc.source_files],
            "total_files": len(doc.source_files),
            "total_log_entries": len(doc.log_entries),
            "total_metric_points": len(doc.metric_points),
            "total_code_artifacts": len(doc.code_artifacts) + len(doc.config_artifacts),
            "overall_time_range_start": ts_all[0] if ts_all else None,
            "overall_time_range_end": ts_all[-1] if ts_all else None,
        }

    @staticmethod
    def build_llm_summary(doc: LOMDocument) -> str:
        """Build a text summary of the parsed LOM data for LLM consumption.
        Truncates and prioritizes error/anomaly content to fit context windows.
        """
        parts = []

        # Source summary
        parts.append(f"=== SOURCE FILES ({len(doc.source_files)} files) ===")
        for sf in doc.source_files:
            parts.append(f"  - {sf.filename} [{sf.file_type}] {sf.size_bytes} bytes, "
                         f"{sf.entries_extracted} entries, status={sf.parse_status}")

        # Log summary (prioritize errors)
        if doc.log_entries:
            errors = [e for e in doc.log_entries if e.level in ("ERROR", "FATAL", "CRITICAL", "SEVERE")]
            warns = [e for e in doc.log_entries if e.level in ("WARN", "WARNING")]
            infos = [e for e in doc.log_entries if e.level in ("INFO", "DEBUG", "TRACE", "NOTICE")]

            parts.append(f"\n=== LOG ENTRIES (total={len(doc.log_entries)}, "
                         f"errors={len(errors)}, warnings={len(warns)}) ===")

            # Show all errors (capped)
            if errors:
                parts.append("\n--- ERROR/FATAL log entries (most important) ---")
                for e in errors[:100]:
                    ts = f"[{e.timestamp}] " if e.timestamp else ""
                    parts.append(f"  {ts}{e.level} ({e.source}): {e.message[:300]}")

            # Show some warnings
            if warns:
                parts.append(f"\n--- WARNING entries (showing {min(30, len(warns))} of {len(warns)}) ---")
                for e in warns[:30]:
                    ts = f"[{e.timestamp}] " if e.timestamp else ""
                    parts.append(f"  {ts}{e.level} ({e.source}): {e.message[:200]}")

            # Show a sample of info logs for context
            if infos:
                parts.append(f"\n--- INFO/DEBUG entries (showing {min(20, len(infos))} of {len(infos)} for context) ---")
                for e in infos[:20]:
                    ts = f"[{e.timestamp}] " if e.timestamp else ""
                    parts.append(f"  {ts}{e.level} ({e.source}): {e.message[:150]}")

        # Metric summary
        if doc.metric_points:
            metrics = {}
            for p in doc.metric_points:
                if p.metric_name not in metrics:
                    metrics[p.metric_name] = []
                metrics[p.metric_name].append(p.value)

            parts.append(f"\n=== METRICS ({len(doc.metric_points)} data points, {len(metrics)} unique metrics) ===")
            for name, values in list(metrics.items())[:20]:
                parts.append(f"  - {name}: min={min(values):.2f}, max={max(values):.2f}, "
                             f"mean={sum(values)/len(values):.2f}, count={len(values)}")

        # Code artifacts
        if doc.code_artifacts:
            parts.append(f"\n=== CODE ARTIFACTS ({len(doc.code_artifacts)} files) ===")
            for ca in doc.code_artifacts:
                parts.append(f"\n--- {ca.filename} ({ca.language}) ---")
                if ca.traceback:
                    parts.append(f"  TRACEBACK FOUND:\n{ca.traceback[:1000]}")
                if ca.error_type:
                    parts.append(f"  Error: {ca.error_type}: {ca.error_message}")
                if ca.functions_detected:
                    parts.append(f"  Functions: {', '.join(ca.functions_detected[:20])}")
                parts.append(f"  Preview:\n{ca.content_preview[:500]}")

        # Config artifacts
        if doc.config_artifacts:
            parts.append(f"\n=== CONFIG FILES ({len(doc.config_artifacts)} files) ===")
            for ca in doc.config_artifacts:
                parts.append(f"\n--- {ca.filename} ---")
                parts.append(ca.content_preview[:500])

        # Raw JSON objects not classified as logs/metrics
        raw_unclassified = len(doc.raw_json_objects) - len(doc.log_entries) - len(doc.metric_points)
        if raw_unclassified > 0:
            parts.append(f"\n=== STRUCTURED DATA OBJECTS ({raw_unclassified} unclassified JSON objects) ===")
            parts.append("These JSON objects did not match log/metric patterns. Analyze them as structured data.")
            for i, obj in enumerate(doc.raw_json_objects[:30]):
                parts.append(f"\n--- Object {i+1} ---")
                parts.append(json.dumps(obj, indent=2, default=str)[:1500])

        # If no log entries AND no metrics AND there are raw JSON objects, add a prominent notice
        if not doc.log_entries and not doc.metric_points and doc.raw_json_objects:
            parts.insert(1, "\n>>> NOTE: No log entries or metrics were detected. "
                           "The uploaded data consists of structured JSON objects. "
                           "Analyze the STRUCTURED DATA OBJECTS section below. <<<\n")

        return "\n".join(parts)
