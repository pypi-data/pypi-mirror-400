"""
CGP SDK Adapters
Framework-specific adapters for agent integration.
"""

from .generic import GenericAdapter

# CrewAI adapter is optional - only import if crewai is installed
try:
    from .crewai import CrewAIAdapter
    __all__ = ["GenericAdapter", "CrewAIAdapter"]
except ImportError:
    __all__ = ["GenericAdapter"]
