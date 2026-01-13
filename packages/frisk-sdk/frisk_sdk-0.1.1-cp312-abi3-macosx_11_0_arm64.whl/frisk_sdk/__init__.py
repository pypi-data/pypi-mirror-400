from enum import Enum

from ._core import ProcessToolCallResultPy, shutdown_instrumentation
from frisk_sdk.core.frisk import Frisk, FriskSession


class ProcessToolCallDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"


__all__ = [
    "ProcessToolCallResultPy",
    "shutdown_instrumentation",
    "ProcessToolCallDecision",
    "Frisk",
    "FriskSession",
]
