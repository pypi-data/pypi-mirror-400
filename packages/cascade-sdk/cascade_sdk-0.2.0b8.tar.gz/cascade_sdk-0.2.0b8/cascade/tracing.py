"""
Core tracing primitives for Cascade SDK
"""
import os
import time
import logging
import threading
import contextvars
from typing import Optional, Dict, Any
from contextlib import contextmanager
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import Tracer, Status, StatusCode

logger = logging.getLogger(__name__)

# Global tracer instance
_tracer: Optional[Tracer] = None
_tracer_provider: Optional[TracerProvider] = None

# Global configuration for trace start events
_cascade_endpoint: Optional[str] = None
_cascade_api_key: Optional[str] = None
_cascade_project: Optional[str] = None

# Context variable for trace metadata
_trace_metadata: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "trace_metadata", default={}
)

# Context variable for current agent name
_current_agent: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_agent", default=None
)


def _send_trace_start(
    trace_id: str,
    root_span_id: str,
    name: str,
    start_time: int,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Send trace start event to backend (non-blocking).
    
    PHASE 3, STEP 3.1 - Real-time trace updates
    
    This function sends an HTTP POST to /api/traces/start when a root span begins.
    It runs in a background thread to avoid blocking trace execution.
    
    Args:
        trace_id: Unique trace identifier (from OTEL span context)
        root_span_id: ID of the root span
        name: Trace/agent name
        start_time: Timestamp in nanoseconds
        metadata: Optional metadata dictionary
    """
    if not _cascade_endpoint or not _cascade_api_key or not _cascade_project:
        # Trace start events disabled (endpoint/API key/project not configured)
        return
    
    def send_async():
        """Background thread function to send trace start event."""
        try:
            import requests
            
            # Build API endpoint URL
            # Remove /v1/traces suffix if present, add /api/traces/start
            base_url = _cascade_endpoint.replace("/v1/traces", "")
            api_url = f"{base_url}/api/traces/start"
            
            # Build request payload
            # Include project like OTLP includes it in resource attributes
            payload = {
                "trace_id": trace_id,
                "root_span_id": root_span_id,
                "name": name,
                "project": _cascade_project,  # From init_tracing(), like OTLP resource_attrs
                "start_time": start_time,
                "metadata": metadata
            }
            
            # Send POST request
            response = requests.post(
                api_url,
                json=payload,
                headers={"X-API-Key": _cascade_api_key},
                timeout=5  # 5 second timeout
            )
            
            if response.status_code == 200:
                logger.debug(f"Trace start event sent successfully: {trace_id} (name='{name}', project='{_cascade_project}')")
            else:
                logger.warning(
                    f"Trace start event failed: {trace_id} "
                    f"(status={response.status_code}, response={response.text})"
                )
        
        except Exception as e:
            # Don't crash if trace start fails - span export will create placeholder
            logger.warning(f"Failed to send trace start event for {trace_id}: {e}")
    
    # Send in background thread (non-blocking)
    thread = threading.Thread(target=send_async, daemon=True)
    thread.start()


def init_tracing(
    project: str,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    environment: Optional[str] = None,
    version: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """
    Initialize OpenTelemetry tracing for Cascade SDK.
    
    Args:
        project: Project name (used for filtering traces)
        endpoint: OTLP endpoint URL (default: https://api.runcascade.com/v1/traces, or CASCADE_ENDPOINT env var)
        api_key: API key for authentication (optional, can also use CASCADE_API_KEY env var)
        metadata: Generic metadata dictionary for any key-value pairs (e.g., {"competition_id": "comp-123"})
        environment: Environment name (e.g., 'dev', 'prod')
        version: Application version
        user_id: User identifier for multi-user scenarios
    """
    global _tracer, _tracer_provider, _cascade_endpoint, _cascade_api_key, _cascade_project
    
    # Use environment variable or parameter for endpoint
    endpoint = endpoint or os.getenv("CASCADE_ENDPOINT", "https://api.runcascade.com/v1/traces")
    
    # Use environment variable or parameter for API key
    api_key = api_key or os.getenv("CASCADE_API_KEY")
    
    # Store in global variables for trace start events (Phase 3)
    _cascade_endpoint = endpoint
    _cascade_api_key = api_key
    _cascade_project = project
    
    # Detect Modal environment
    is_modal = os.getenv("MODAL_ENVIRONMENT") is not None
    if is_modal and endpoint == "http://localhost:8000/v1/traces":
        import warnings
        warnings.warn(
            "Running in Modal environment but no CASCADE_ENDPOINT configured. "
            "Traces will not be sent. Set CASCADE_ENDPOINT to your tunnel URL.",
            UserWarning
        )
    
    # Build resource attributes
    resource_attributes = {
        "service.name": project,
        "cascade.project": project,
        "cascade.environment": environment or "local",
    }
    
    if environment:
        resource_attributes["deployment.environment"] = environment
    if version:
        resource_attributes["service.version"] = version
    if user_id:
        resource_attributes["cascade.user_id"] = user_id
    
    # Add all metadata as resource attributes with cascade. prefix
    # This allows any customer to pass any metadata they need
    if metadata:
        for key, value in metadata.items():
            resource_attributes[f"cascade.{key}"] = str(value)
    
    # Create resource
    resource = Resource.create(resource_attributes)
    
    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)
    
    # Build headers for API key authentication
    headers = None
    if api_key:
        headers = {"authorization": f"Bearer {api_key}"}
    
    # Create OTLP HTTP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        headers=headers,
    )
    
    # Add span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    _tracer_provider.add_span_processor(span_processor)
    
    # Set global tracer provider
    trace.set_tracer_provider(_tracer_provider)
    
    # Get tracer instance
    _tracer = trace.get_tracer(__name__)


def get_tracer() -> Optional[Tracer]:
    """Get the global tracer instance."""
    return _tracer


def get_current_agent() -> Optional[str]:
    """Get the currently active agent name from context."""
    return _current_agent.get()


@contextmanager
def trace_run(
    name: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for tracing agent execution.
    
    Creates a root span for the agent run and maintains trace context.
    
    Args:
        name: Name of the agent/function being traced
        metadata: Additional metadata to attach to the span (e.g., session_id, user_id, request_id)
    
    Example:
        ```python
        with trace_run("MyAgent", metadata={"task_id": "123"}):
            # Your agent code here
            pass
        ```
    """
    if _tracer is None:
        raise RuntimeError(
            "Tracing not initialized. Call init_tracing() first."
        )
    
    metadata = metadata or {}
    
    # Store metadata in context
    _trace_metadata.set(metadata)
    
    # Start root span - start_as_current_span returns a context manager
    with _tracer.start_as_current_span(name, kind=trace.SpanKind.SERVER) as span_context:
        # Get the actual span from the current context
        span = trace.get_current_span()
        
        try:
            # Add metadata as span attributes
            for key, value in metadata.items():
                if value is not None:
                    span.set_attribute(f"cascade.{key}", str(value))
            
            # Set span attributes
            span.set_attribute("cascade.span_type", "function")
            
            # ========================================
            # PHASE 3, STEP 3.2: Send trace start event
            # ========================================
            # Extract trace and span IDs from OpenTelemetry span context
            span_ctx = span.get_span_context()
            trace_id = format(span_ctx.trace_id, '032x')  # Convert to 32-char hex string
            span_id = format(span_ctx.span_id, '016x')    # Convert to 16-char hex string
            start_time = time.time_ns()  # Current time in nanoseconds
            
            # Send trace start event to backend (non-blocking)
            _send_trace_start(
                trace_id=trace_id,
                root_span_id=span_id,
                name=name,
                start_time=start_time,
                metadata=metadata
            )
            
            yield span
            
            # Mark span as successful
            span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            # Mark span as error
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise


@contextmanager
def trace_agent(
    agent_name: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for tracing agent execution.
    
    Creates a span for the agent and sets it as the current agent context.
    All tools and LLM calls within this context will be tagged with the agent name.
    
    Args:
        agent_name: Name of the agent (e.g., "ExplorerAgent", "EvaluatorAgent")
        metadata: Additional metadata to attach to the agent span (e.g., {"loop": 1})
    
    Example:
        ```python
        with trace_agent("EvaluatorAgent", metadata={"loop": 1}):
            # Run evaluator logic
            result = evaluator.run()
            # All tool calls and LLM calls here will be tagged with agent="EvaluatorAgent"
        ```
    """
    if _tracer is None:
        raise RuntimeError(
            "Tracing not initialized. Call init_tracing() first."
        )
    
    metadata = metadata or {}
    
    # Set current agent in context
    token = _current_agent.set(agent_name)
    
    try:
        # Create agent span
        with _tracer.start_as_current_span(
            agent_name, 
            kind=trace.SpanKind.INTERNAL
        ) as span_context:
            span = trace.get_current_span()
            
            try:
                # Set agent-specific attributes
                span.set_attribute("cascade.span_type", "agent")
                span.set_attribute("cascade.agent_name", agent_name)
                
                # Add metadata
                for key, value in metadata.items():
                    if value is not None:
                        span.set_attribute(f"agent.{key}", str(value))
                
                yield span
                
                span.set_status(Status(StatusCode.OK))
                
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    finally:
        # Reset agent context
        _current_agent.reset(token)

