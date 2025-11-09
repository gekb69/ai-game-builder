"""
OpenTelemetry Integration for Distributed Tracing
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.prometheus import PrometheusMetricsExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
import prometheus_client

def setup_telemetry(app, service_name: str = "SelfAwareAI-v100"):
    """Setup OpenTelemetry for FastAPI and Celery"""

    # Resource
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "v100"
    })

    # Tracer
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)

    # Metrics
    prometheus_client.start_http_server(9091)
    metrics_exporter = PrometheusMetricsExporter()
    meter_provider = MeterProvider(resource=resource)
    meter_provider.start_pipeline(metrics_exporter)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument Celery
    CeleryInstrumentor().instrument()

    # Instrument Redis
    RedisInstrumentor().instrument()

    return tracer
