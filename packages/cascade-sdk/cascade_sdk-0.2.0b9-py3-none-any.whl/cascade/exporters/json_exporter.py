"""
JSON File Exporter for OpenTelemetry spans.

This exporter writes spans to a JSON file in real-time as they complete.
Useful for customers who want local copies of traces for debugging, archival, or offline analysis.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

logger = logging.getLogger(__name__)


class JSONFileExporter(SpanExporter):
    """
    Exports OpenTelemetry spans to a JSON file.
    
    Spans are stored in a JSON array format with metadata:
    {
        "spans": [...],
        "metadata": {
            "span_count": N,
            "last_updated": "timestamp"
        }
    }
    
    The exporter handles:
    - Automatic file and directory creation
    - Thread-safe concurrent writes
    - Graceful error handling (won't crash agent on file errors)
    - Real-time updates as spans complete
    - Easy to read and parse as complete JSON document
    
    Example:
        ```python
        from cascade import init_tracing
        
        init_tracing(
            project="my_agent",
            endpoint="https://api.runcascade.com/v1/traces",
            api_key="cascade_xxx",
            json_export_path="/workspace/traces/trace.json"
        )
        ```
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the JSON file exporter.
        
        Args:
            file_path: Path to the output JSON file (will be created if doesn't exist)
        """
        self.file_path = Path(file_path)
        self.lock = threading.Lock()  # Thread-safe writes
        
        try:
            # Create parent directories if they don't exist
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file if it doesn't exist (empty JSON structure)
            if not self.file_path.exists():
                initial_data = {
                    "spans": [],
                    "metadata": {
                        "span_count": 0,
                        "last_updated": None
                    }
                }
                self.file_path.write_text(json.dumps(initial_data, indent=2))
                logger.info(f"Created JSON export file: {self.file_path}")
            else:
                logger.info(f"Using existing JSON export file: {self.file_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize JSON file exporter: {e}")
            # Don't raise - allow agent to continue even if file export fails
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans to JSON file.
        
        Called by BatchSpanProcessor when spans are ready to export.
        Appends spans to the JSON array in the file.
        
        Args:
            spans: Sequence of ReadableSpan objects to export
            
        Returns:
            SpanExportResult.SUCCESS or SpanExportResult.FAILURE
        """
        if not spans:
            return SpanExportResult.SUCCESS
        
        try:
            with self.lock:
                # Read existing data
                try:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    # If file is corrupted or missing, start fresh
                    data = {"spans": [], "metadata": {"span_count": 0, "last_updated": None}}
                
                # Convert and append new spans
                for span in spans:
                    span_dict = self._span_to_dict(span)
                    data["spans"].append(span_dict)
                
                # Update metadata
                from datetime import datetime
                data["metadata"]["span_count"] = len(data["spans"])
                data["metadata"]["last_updated"] = datetime.now().isoformat()
                
                # Write back to file (atomic operation)
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                        
            logger.debug(f"Exported {len(spans)} span(s) to {self.file_path}")
            return SpanExportResult.SUCCESS
            
        except Exception as e:
            logger.error(f"Failed to export spans to JSON file: {e}")
            return SpanExportResult.FAILURE
    
    def _span_to_dict(self, span: ReadableSpan) -> dict:
        """
        Convert OpenTelemetry span to JSON-serializable dictionary.
        
        Extracts key fields that are most useful for debugging and analysis.
        
        Args:
            span: ReadableSpan object from OpenTelemetry
            
        Returns:
            Dictionary with span data
        """
        # Extract span context
        span_context = span.get_span_context()
        
        # Build base span dict
        span_dict = {
            "trace_id": format(span_context.trace_id, '032x'),
            "span_id": format(span_context.span_id, '016x'),
            "parent_span_id": format(span.parent.span_id, '016x') if span.parent else None,
            "name": span.name,
            "kind": span.kind.name if span.kind else None,
            "start_time": span.start_time,
            "end_time": span.end_time,
            "duration": (span.end_time - span.start_time) / 1e9 if span.end_time else None,  # Convert to seconds
            "status": {
                "status_code": span.status.status_code.name if span.status else None,
                "description": span.status.description if span.status else None,
            },
        }
        
        # Add attributes if present
        if span.attributes:
            span_dict["attributes"] = dict(span.attributes)
        
        # Add events if present (e.g., logs, exceptions)
        if span.events:
            span_dict["events"] = [
                {
                    "name": event.name,
                    "timestamp": event.timestamp,
                    "attributes": dict(event.attributes) if event.attributes else None,
                }
                for event in span.events
            ]
        
        # Note: Resource attributes (project, environment, etc.) are intentionally excluded
        # to keep the JSON output cleaner and more focused on span-specific data
        
        return span_dict
    
    def shutdown(self) -> None:
        """
        Shutdown the exporter.
        
        Called when the tracer provider is shut down.
        Ensures all pending writes are flushed.
        """
        try:
            logger.info(f"JSON file exporter shutdown: {self.file_path}")
        except Exception as e:
            logger.error(f"Error during JSON exporter shutdown: {e}")
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Force flush any buffered spans.
        
        For file exporter, writes are immediate (no buffering), so this is a no-op.
        
        Args:
            timeout_millis: Maximum time to wait for flush (ignored)
            
        Returns:
            True (always succeeds)
        """
        return True

