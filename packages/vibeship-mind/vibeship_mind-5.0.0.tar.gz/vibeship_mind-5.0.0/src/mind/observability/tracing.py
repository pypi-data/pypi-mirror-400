"""OpenTelemetry tracing for Mind v5.

Provides distributed tracing for decision-to-outcome journey:
- HTTP request tracing (FastAPI instrumentation)
- Memory retrieval tracing
- Causal graph query tracing
- Event publishing tracing

Configuration via environment variables:
- OTEL_EXPORTER_OTLP_ENDPOINT: OTLP collector endpoint (e.g., http://tempo:4318)
- OTEL_EXPORTER_OTLP_PROTOCOL: Protocol (http/protobuf or grpc), default: http/protobuf
- OTEL_TRACES_SAMPLER: Sampler type (always_on, always_off, traceidratio)
- OTEL_TRACES_SAMPLER_ARG: Sampler argument (e.g., 0.1 for 10% sampling)
- JAEGER_AGENT_HOST: Jaeger agent host (for Jaeger-specific exporter)
- JAEGER_AGENT_PORT: Jaeger agent port (default: 6831)

Supported backends:
- Jaeger (via OTLP or Jaeger Thrift)
- Grafana Tempo (via OTLP)
- Any OTLP-compatible collector
"""

import os

import structlog
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.sampling import (
    ALWAYS_OFF,
    ALWAYS_ON,
    ParentBased,
    Sampler,
    TraceIdRatioBased,
)
from opentelemetry.trace import Span, Status, StatusCode, Tracer

logger = structlog.get_logger()

# Global tracer provider
_tracer_provider: TracerProvider | None = None
_initialized: bool = False


def _get_sampler(environment: str) -> Sampler:
    """Get trace sampler based on configuration.

    Args:
        environment: Deployment environment

    Returns:
        Configured Sampler
    """
    sampler_type = os.environ.get("OTEL_TRACES_SAMPLER", "").lower()
    sampler_arg = os.environ.get("OTEL_TRACES_SAMPLER_ARG", "1.0")

    if sampler_type == "always_off":
        return ALWAYS_OFF
    elif sampler_type == "traceidratio":
        try:
            ratio = float(sampler_arg)
            # Use ParentBased to respect parent sampling decisions
            return ParentBased(TraceIdRatioBased(ratio))
        except ValueError:
            logger.warning("invalid_sampler_ratio", value=sampler_arg)
            return ALWAYS_ON
    elif sampler_type == "always_on" or not sampler_type:
        # Default behavior based on environment
        if environment == "production":
            # Sample 10% in production by default
            return ParentBased(TraceIdRatioBased(0.1))
        elif environment == "staging":
            # Sample 50% in staging
            return ParentBased(TraceIdRatioBased(0.5))
        else:
            # Sample everything in development
            return ALWAYS_ON

    return ALWAYS_ON


def _configure_otlp_exporter(provider: TracerProvider, endpoint: str) -> bool:
    """Configure OTLP exporter (HTTP or gRPC).

    Args:
        provider: TracerProvider to add exporter to
        endpoint: OTLP endpoint URL

    Returns:
        True if exporter was configured successfully
    """
    protocol = os.environ.get("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf").lower()

    if protocol == "grpc":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

            otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info("tracing_otlp_grpc_configured", endpoint=endpoint)
            return True
        except ImportError:
            logger.warning("tracing_otlp_grpc_unavailable", reason="grpc exporter not installed")
    else:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            # Ensure endpoint includes the traces path
            traces_endpoint = endpoint
            if not endpoint.endswith("/v1/traces"):
                traces_endpoint = f"{endpoint.rstrip('/')}/v1/traces"

            otlp_exporter = OTLPSpanExporter(endpoint=traces_endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info("tracing_otlp_http_configured", endpoint=traces_endpoint)
            return True
        except ImportError:
            logger.warning("tracing_otlp_http_unavailable", reason="http exporter not installed")

    return False


def _configure_jaeger_exporter(provider: TracerProvider) -> bool:
    """Configure Jaeger Thrift exporter (legacy).

    Args:
        provider: TracerProvider to add exporter to

    Returns:
        True if exporter was configured successfully
    """
    jaeger_host = os.environ.get("JAEGER_AGENT_HOST")
    if not jaeger_host:
        return False

    try:
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter

        jaeger_port = int(os.environ.get("JAEGER_AGENT_PORT", "6831"))
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        logger.info("tracing_jaeger_configured", host=jaeger_host, port=jaeger_port)
        return True
    except ImportError:
        logger.warning("tracing_jaeger_unavailable", reason="jaeger exporter not installed")
        return False


def configure_tracing(
    service_name: str = "mind-v5",
    service_version: str = "5.0.0",
    environment: str = "development",
) -> TracerProvider:
    """Configure OpenTelemetry tracing.

    Supports multiple exporters with automatic fallback:
    1. OTLP (HTTP or gRPC) - for Jaeger, Tempo, or any OTLP collector
    2. Jaeger Thrift - legacy Jaeger agent support
    3. Console - for local development

    Args:
        service_name: Name of the service for traces
        service_version: Version of the service
        environment: Deployment environment (development, staging, production)

    Returns:
        Configured TracerProvider
    """
    global _tracer_provider, _initialized

    if _initialized:
        return _tracer_provider

    # Get sampler based on environment and configuration
    sampler = _get_sampler(environment)

    # Create resource with service info
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "deployment.environment": environment,
            "service.namespace": "mind",
        }
    )

    # Create tracer provider with sampler
    _tracer_provider = TracerProvider(resource=resource, sampler=sampler)

    # Configure exporters (try in order of preference)
    exporter_configured = False

    # 1. Try OTLP endpoint
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        exporter_configured = _configure_otlp_exporter(_tracer_provider, otlp_endpoint)

    # 2. Try Jaeger agent (legacy)
    if not exporter_configured:
        exporter_configured = _configure_jaeger_exporter(_tracer_provider)

    # 3. Fall back to console in development
    if not exporter_configured:
        if environment == "development":
            console_exporter = ConsoleSpanExporter()
            _tracer_provider.add_span_processor(SimpleSpanProcessor(console_exporter))
            logger.info("tracing_console_configured")
        else:
            logger.info("tracing_disabled", reason="no exporter configured")

    # Set as global provider
    trace.set_tracer_provider(_tracer_provider)

    _initialized = True
    logger.info(
        "tracing_initialized",
        service=service_name,
        version=service_version,
        environment=environment,
        sampler=type(sampler).__name__,
    )

    return _tracer_provider


def get_tracer(name: str = "mind") -> Tracer:
    """Get a tracer instance.

    Args:
        name: Name for the tracer (e.g., "mind.memory", "mind.decision")

    Returns:
        OpenTelemetry Tracer
    """
    return trace.get_tracer(name)


def instrument_fastapi(app) -> None:
    """Instrument FastAPI application for automatic tracing.

    Args:
        app: FastAPI application instance
    """
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="health,ready,metrics",  # Skip health/metrics endpoints
    )
    logger.info("fastapi_instrumented")


def uninstrument_fastapi(app) -> None:
    """Remove FastAPI instrumentation.

    Args:
        app: FastAPI application instance
    """
    try:
        FastAPIInstrumentor.uninstrument_app(app)
        logger.info("fastapi_uninstrumented")
    except Exception as e:
        logger.warning("fastapi_uninstrument_failed", error=str(e))


def shutdown_tracing() -> None:
    """Shutdown tracing and flush pending spans."""
    global _tracer_provider, _initialized

    if _tracer_provider:
        _tracer_provider.shutdown()
        logger.info("tracing_shutdown")

    _tracer_provider = None
    _initialized = False


# Convenience decorators and context managers


class SpanContext:
    """Context manager for creating spans with automatic error handling."""

    def __init__(
        self,
        name: str,
        tracer_name: str = "mind",
        attributes: dict | None = None,
    ):
        self.name = name
        self.tracer_name = tracer_name
        self.attributes = attributes or {}
        self.span: Span | None = None

    def __enter__(self) -> Span:
        tracer = get_tracer(self.tracer_name)
        self.span = tracer.start_span(self.name)

        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)

        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.record_exception(exc_val)
            else:
                self.span.set_status(Status(StatusCode.OK))
            self.span.end()
        return False


class AsyncSpanContext:
    """Async context manager for creating spans with automatic error handling."""

    def __init__(
        self,
        name: str,
        tracer_name: str = "mind",
        attributes: dict | None = None,
    ):
        self.name = name
        self.tracer_name = tracer_name
        self.attributes = attributes or {}
        self.span: Span | None = None

    async def __aenter__(self) -> Span:
        tracer = get_tracer(self.tracer_name)
        self.span = tracer.start_span(self.name)

        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)

        return self.span

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.record_exception(exc_val)
            else:
                self.span.set_status(Status(StatusCode.OK))
            self.span.end()
        return False


def trace_operation(name: str, tracer_name: str = "mind"):
    """Decorator for tracing async functions.

    Usage:
        @trace_operation("retrieve_memories", "mind.memory")
        async def retrieve_memories(query: str) -> List[Memory]:
            ...
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with AsyncSpanContext(name, tracer_name) as span:
                # Add function args as attributes (excluding sensitive data)
                for i, arg in enumerate(args[:3]):  # First 3 positional args
                    if not _is_sensitive(arg):
                        span.set_attribute(f"arg_{i}", str(arg)[:100])

                result = await func(*args, **kwargs)

                # Add result info
                if hasattr(result, "is_ok"):
                    span.set_attribute("result.ok", result.is_ok)

                return result

        return wrapper

    return decorator


def _is_sensitive(value) -> bool:
    """Check if a value might contain sensitive data."""
    if isinstance(value, str):
        sensitive_keywords = ["password", "secret", "key", "token", "auth"]
        lower_val = value.lower()
        return any(kw in lower_val for kw in sensitive_keywords)
    return False
