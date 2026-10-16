"""Opt-in local OTLP. No request bodies, credentials, task text or user IDs as attributes."""

import os

from opentelemetry import metrics, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

_configured = False


def configure():
    global _configured
    if _configured:
        return
    _configured = True
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    if not endpoint:
        return
    from urllib.parse import urlsplit

    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"collector", "localhost", "127.0.0.1"}
        or parsed.username
        or parsed.query
    ):
        raise ValueError("Only an explicit local OTLP endpoint is allowed")
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create(
        {
            "service.name": os.environ.get("OTEL_SERVICE_NAME", "nova-fastapi"),
            "deployment.environment.name": "local",
        }
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint + "/v1/traces", timeout=2))
    )
    trace.set_tracer_provider(provider)
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint + "/v1/metrics", timeout=2),
        export_interval_millis=5000,
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))


def observe(method, status, seconds, route):
    meter = metrics.get_meter("nova.http")
    attributes = {
        "http.request.method": method,
        "http.response.status_code": status,
        "http.route": route,
    }
    meter.create_counter("nova.http.requests").add(1, attributes)
    meter.create_histogram("nova.http.duration", unit="s").record(seconds, attributes)
