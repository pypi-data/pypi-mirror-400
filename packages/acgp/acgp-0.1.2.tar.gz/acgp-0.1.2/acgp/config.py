"""
ACGP SDK Configuration

Configuration management for the Agentic Cognitive Governance Protocol SDK.
Supports environment variables, explicit configuration, and sensible defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ACGPConfig:
    """
    Configuration for the ACGP SDK client.

    All settings can be overridden via environment variables with ACGP_ prefix.
    Example: ACGP_API_KEY, ACGP_ENDPOINT, ACGP_FLUSH_INTERVAL
    """

    # Required
    api_key: str = field(default="")

    # Endpoint configuration
    endpoint: str = field(default="https://api.steward-agent.com")
    api_version: str = field(default="v1")

    # Batching and transport
    flush_interval: float = field(default=5.0)  # seconds
    batch_size: int = field(default=100)  # events per batch
    max_queue_size: int = field(default=10000)  # local buffer limit

    # Retry configuration
    max_retries: int = field(default=3)
    retry_base_delay: float = field(default=1.0)  # seconds
    retry_max_delay: float = field(default=30.0)  # seconds

    # Timeouts
    connect_timeout: float = field(default=5.0)  # seconds
    read_timeout: float = field(default=30.0)  # seconds

    # Behavior
    enabled: bool = field(default=True)  # Master switch to disable SDK
    fail_silently: bool = field(default=True)  # Don't raise on transport errors
    debug: bool = field(default=False)  # Enable debug logging

    def __post_init__(self):
        """Load environment variables after initialization."""
        self._load_from_environment()
        self._validate()

    def _load_from_environment(self):
        """Override settings from environment variables."""
        env_mappings = {
            "ACGP_API_KEY": ("api_key", str),
            "ACGP_ENDPOINT": ("endpoint", str),
            "ACGP_API_VERSION": ("api_version", str),
            "ACGP_FLUSH_INTERVAL": ("flush_interval", float),
            "ACGP_BATCH_SIZE": ("batch_size", int),
            "ACGP_MAX_QUEUE_SIZE": ("max_queue_size", int),
            "ACGP_MAX_RETRIES": ("max_retries", int),
            "ACGP_RETRY_BASE_DELAY": ("retry_base_delay", float),
            "ACGP_RETRY_MAX_DELAY": ("retry_max_delay", float),
            "ACGP_CONNECT_TIMEOUT": ("connect_timeout", float),
            "ACGP_READ_TIMEOUT": ("read_timeout", float),
            "ACGP_ENABLED": ("enabled", lambda x: x.lower() in ("true", "1", "yes")),
            "ACGP_FAIL_SILENTLY": ("fail_silently", lambda x: x.lower() in ("true", "1", "yes")),
            "ACGP_DEBUG": ("debug", lambda x: x.lower() in ("true", "1", "yes")),
        }

        for env_var, (attr, converter) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    setattr(self, attr, converter(value))
                except (ValueError, TypeError):
                    pass  # Keep default if conversion fails

    def _validate(self):
        """Validate configuration values."""
        if self.flush_interval <= 0:
            raise ValueError("flush_interval must be positive")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.max_queue_size <= 0:
            raise ValueError("max_queue_size must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")

    @property
    def base_url(self) -> str:
        """Get the full base URL for API calls."""
        endpoint = self.endpoint.rstrip("/")
        return f"{endpoint}/{self.api_version}"

    def is_configured(self) -> bool:
        """Check if the SDK is properly configured with an API key."""
        return bool(self.api_key)


def load_config(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    **kwargs
) -> ACGPConfig:
    """
    Load SDK configuration with optional overrides.

    Priority (highest to lowest):
    1. Environment variables
    2. Explicit parameters
    3. Default values

    Args:
        api_key: API key for authentication
        endpoint: Backend API endpoint
        **kwargs: Additional configuration options

    Returns:
        ACGPConfig instance
    """
    config_kwargs = {}

    if api_key is not None:
        config_kwargs["api_key"] = api_key
    if endpoint is not None:
        config_kwargs["endpoint"] = endpoint

    config_kwargs.update(kwargs)

    return ACGPConfig(**config_kwargs)
