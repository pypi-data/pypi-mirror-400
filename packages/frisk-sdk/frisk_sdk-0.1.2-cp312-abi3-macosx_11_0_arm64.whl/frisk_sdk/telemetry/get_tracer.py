from __future__ import annotations

from opentelemetry import trace
from opentelemetry.trace import Tracer


def get_tracer() -> Tracer:
    return trace.get_tracer("frisk_python_sdk")
