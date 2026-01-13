"""
CGP SDK Wrapper Module
Agent wrapping utilities for transparent monitoring.
"""

from .agent_protocol import (
    MonitorableAgent,
    AgentAdapter,
    AgentExecutionContext,
    AgentExecutionResult,
)

__all__ = [
    "MonitorableAgent",
    "AgentAdapter",
    "AgentExecutionContext",
    "AgentExecutionResult",
]
