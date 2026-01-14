"""
OpenTelemetry Sidecar - Observability integration for PTR Engine

This module provides OpenTelemetry-based observability for the PTR runtime,
enabling distributed tracing, metrics, and logging across all REPL phases.

REPL Phase Instrumentation:
- prep: Log V_pre validation status, trace artifact loading
- exec: Metrics (CPU, memory, duration), trace execution path
- post: Log verification results, trace VCard generation
- await: Event for handle_history recording

See Also:
- CLM_MCard_REPL_Implementation.md §11: Grafana LGTM Integration
- PTR_MCard_CLM_Recent_Developments_Jan2026.md §6.2: Universal Observability
"""

import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timezone
from functools import wraps
from contextlib import contextmanager

# OpenTelemetry imports (with fallback if not installed)
try:
    from opentelemetry import trace, metrics
    from opentelemetry.trace import Tracer, Span, SpanKind, Status, StatusCode
    from opentelemetry.metrics import Meter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    Tracer = None
    Span = None
    Meter = None


class REPLPhase:
    """Enum-like class for REPL phases."""
    PREP = "prep"
    EXEC = "exec"
    POST = "post"
    AWAIT = "await"


class OpenTelemetrySidecar:
    """
    OpenTelemetry Sidecar for PTR Engine observability.
    
    Provides instrumentation hooks for each REPL phase:
    - prep: Artifact loading, V_pre validation
    - exec: CLM execution, sandbox runtime
    - post: Balanced verification, VCard generation
    - await: Handle history recording, state transition
    
    Usage:
        sidecar = OpenTelemetrySidecar.get_instance()
        sidecar.initialize({
            "endpoint": "http://localhost:4317",
            "service_name": "ptr-runtime",
            "service_version": "1.0.0"
        })
        
        with sidecar.trace_phase(REPLPhase.PREP, pcard_hash="abc123"):
            # do prep work
            pass
    """
    
    _instance: Optional["OpenTelemetrySidecar"] = None
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._tracer: Optional[Tracer] = None
        self._meter: Optional[Meter] = None
        self._config: Dict[str, Any] = {}
        
        # Metrics
        self._phase_duration_histogram = None
        self._phase_counter = None
        self._error_counter = None
        
    @classmethod
    def get_instance(cls) -> "OpenTelemetrySidecar":
        """Get singleton instance of OpenTelemetrySidecar."""
        if cls._instance is None:
            cls._instance = OpenTelemetrySidecar()
        return cls._instance
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize OpenTelemetry with provided configuration.
        
        Args:
            config: Configuration dictionary with keys:
                - endpoint: OTLP endpoint (e.g., "http://localhost:4317")
                - service_name: Name of the service
                - service_version: Version of the service
                - namespace: Optional namespace prefix
                
        Returns:
            True if initialization succeeded, False otherwise
        """
        if not OTEL_AVAILABLE:
            self.logger.warning(
                "[OpenTelemetrySidecar] OpenTelemetry SDK not installed. "
                "Install with: pip install opentelemetry-sdk opentelemetry-exporter-otlp"
            )
            return False
        
        if self._initialized:
            self.logger.warning("[OpenTelemetrySidecar] Already initialized")
            return True
            
        self._config = config
        endpoint = config.get("endpoint", "http://localhost:4317")
        service_name = config.get("service_name", "ptr-runtime")
        service_version = config.get("service_version", "1.0.0")
        namespace = config.get("namespace", "ptr")
        
        try:
            # Set up tracer provider
            tracer_provider = TracerProvider()
            span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
            tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
            trace.set_tracer_provider(tracer_provider)
            self._tracer = trace.get_tracer(service_name, service_version)
            
            # Set up meter provider
            metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
            metric_reader = PeriodicExportingMetricReader(metric_exporter)
            meter_provider = MeterProvider(metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)
            self._meter = metrics.get_meter(service_name, service_version)
            
            # Create metrics instruments
            self._phase_duration_histogram = self._meter.create_histogram(
                name=f"{namespace}.repl.phase.duration",
                description="Duration of REPL phase execution in milliseconds",
                unit="ms"
            )
            
            self._phase_counter = self._meter.create_counter(
                name=f"{namespace}.repl.phase.count",
                description="Count of REPL phase executions"
            )
            
            self._error_counter = self._meter.create_counter(
                name=f"{namespace}.repl.error.count",
                description="Count of errors during REPL execution"
            )
            
            self._initialized = True
            self.logger.info(
                f"[OpenTelemetrySidecar] Initialized for {service_name}@{service_version} "
                f"-> {endpoint}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"[OpenTelemetrySidecar] Initialization failed: {e}")
            return False
    
    @contextmanager
    def trace_phase(
        self, 
        phase: str, 
        pcard_hash: Optional[str] = None,
        target_hash: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for tracing a REPL phase.
        
        Args:
            phase: One of REPLPhase.PREP, EXEC, POST, AWAIT
            pcard_hash: Optional PCard hash for context
            target_hash: Optional target hash for context
            attributes: Optional additional attributes
            
        Yields:
            The active span (or None if not initialized)
        """
        if not self._initialized or not self._tracer:
            yield None
            return
            
        span_name = f"ptr.repl.{phase}"
        span_attributes = {
            "repl.phase": phase,
            "ptr.pcard_hash": pcard_hash or "",
            "ptr.target_hash": target_hash or "",
        }
        if attributes:
            span_attributes.update(attributes)
            
        start_time = datetime.now(timezone.utc)
        
        with self._tracer.start_as_current_span(
            span_name, 
            kind=SpanKind.INTERNAL,
            attributes=span_attributes
        ) as span:
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                self._record_error(phase)
                raise
            finally:
                end_time = datetime.now(timezone.utc)
                duration_ms = (end_time - start_time).total_seconds() * 1000
                self._record_phase_duration(phase, duration_ms)
                self._record_phase_count(phase)
    
    def log_event(
        self, 
        phase: str, 
        event_name: str, 
        attributes: Optional[Dict[str, Any]] = None
    ):
        """
        Log an event within a REPL phase.
        
        Args:
            phase: The current REPL phase
            event_name: Name of the event
            attributes: Optional event attributes
        """
        if not self._initialized or not self._tracer:
            self.logger.info(f"[{phase}] {event_name}: {attributes}")
            return
            
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(
                event_name,
                attributes=attributes or {}
            )
    
    def _record_phase_duration(self, phase: str, duration_ms: float):
        """Record phase duration metric."""
        if self._phase_duration_histogram:
            self._phase_duration_histogram.record(
                duration_ms,
                attributes={"repl.phase": phase}
            )
    
    def _record_phase_count(self, phase: str):
        """Record phase execution count."""
        if self._phase_counter:
            self._phase_counter.add(1, attributes={"repl.phase": phase})
    
    def _record_error(self, phase: str):
        """Record error count."""
        if self._error_counter:
            self._error_counter.add(1, attributes={"repl.phase": phase})
    
    def is_initialized(self) -> bool:
        """Check if sidecar is initialized."""
        return self._initialized
    
    def get_tracer(self) -> Optional[Tracer]:
        """Get the underlying tracer instance."""
        return self._tracer
    
    def get_meter(self) -> Optional[Meter]:
        """Get the underlying meter instance."""
        return self._meter


# Convenience decorator for phase instrumentation
def instrument_phase(phase: str):
    """
    Decorator to instrument a function as a REPL phase.
    
    Usage:
        @instrument_phase(REPLPhase.PREP)
        def _prep(self, pcard_hash, target_hash):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            sidecar = OpenTelemetrySidecar.get_instance()
            
            # Extract common attributes
            pcard_hash = kwargs.get('pcard_hash') or (args[0] if args else None)
            target_hash = kwargs.get('target_hash') or (args[1] if len(args) > 1 else None)
            
            with sidecar.trace_phase(phase, pcard_hash, target_hash):
                return func(self, *args, **kwargs)
        return wrapper
    return decorator
