"""
CrewAI instrumentation module for FloTorch tracing.

This module provides OpenTelemetry instrumentation for CrewAI agents,
tasks, and workflows.
"""

from .listeners import FloTorchCrewAIEventListener

__all__ = [
    "FloTorchCrewAIEventListener",
]
