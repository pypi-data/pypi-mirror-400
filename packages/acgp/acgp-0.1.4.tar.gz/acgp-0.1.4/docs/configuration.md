# Configuration Guide

Complete guide to configuring the CGP SDK.

## Configuration Priority

Configuration values are loaded in this order (highest priority first):

1. **Explicit parameters** passed to `CGPClient()`
2. **Environment variables** (prefixed with `CGP_`)
3. **Default values**

## Environment Variables

### Required

```bash
# Your Steward Agent API key
CGP_API_KEY=sk_live_xxxxxxxxxxxxxxxx

# Backend API endpoint
CGP_ENDPOINT=https://api.steward-agent.com
```

### Optional

```bash
# Master switch to enable/disable SDK (default: true)
CGP_ENABLED=true

# Enable debug logging (default: false)
CGP_DEBUG=false

# Suppress exceptions, log errors instead (default: true)
CGP_FAIL_SILENTLY=true
```

### Batching & Queue

```bash
# Seconds between automatic flushes (default: 5.0)
CGP_FLUSH_INTERVAL=5.0

# Maximum traces per batch (default: 100)
CGP_BATCH_SIZE=100

# Maximum traces in local queue (default: 10000)
CGP_MAX_QUEUE_SIZE=10000
```

### Retry & Timeouts

```bash
# Maximum retry attempts (default: 3)
CGP_MAX_RETRIES=3

# Base delay between retries in seconds (default: 1.0)
CGP_RETRY_BASE_DELAY=1.0

# Maximum retry delay in seconds (default: 30.0)
CGP_RETRY_MAX_DELAY=30.0

# Connection timeout in seconds (default: 5.0)
CGP_CONNECT_TIMEOUT=5.0

# Read timeout in seconds (default: 30.0)
CGP_READ_TIMEOUT=30.0
```

## Programmatic Configuration

### Basic Setup

```python
from cgp_sdk import CGPClient

client = CGPClient(
    api_key="sk_live_...",
    endpoint="https://api.steward-agent.com",
    debug=True,
)
```

### Full Configuration

```python
from cgp_sdk import CGPClient, SSEConfig

def handle_feedback(trace_id, data):
    print(f"Feedback: {data}")

def handle_flush(results):
    print(f"Flushed {len(results)} batches")

client = CGPClient(
    # Authentication
    api_key="sk_live_...",
    endpoint="https://api.steward-agent.com",

    # Callbacks
    on_feedback=handle_feedback,      # Real-time SSE feedback
    on_flush_complete=handle_flush,   # After each batch flush

    # SSE configuration
    sse_config=SSEConfig(
        reconnect_delay=1.0,
        max_reconnect_delay=30.0,
        connection_timeout=10.0,
        read_timeout=300.0,
    ),

    # Behavior
    enabled=True,                     # Master switch
    debug=False,                      # Debug logging
    fail_silently=True,               # Don't raise exceptions

    # Batching
    flush_interval=5.0,               # Auto-flush interval
    batch_size=100,                   # Traces per batch
    max_queue_size=10000,             # Queue limit

    # Retry
    max_retries=3,
    retry_base_delay=1.0,
    retry_max_delay=30.0,

    # Timeouts
    connect_timeout=5.0,
    read_timeout=30.0,
)
```

## SSE Configuration

Customize Server-Sent Events streaming behavior:

```python
from cgp_sdk import SSEConfig

sse_config = SSEConfig(
    # Initial delay before reconnecting after disconnect
    reconnect_delay=1.0,

    # Maximum reconnect delay (uses exponential backoff)
    max_reconnect_delay=30.0,

    # Timeout for establishing connection
    connection_timeout=10.0,

    # Timeout for reading data (long for SSE)
    read_timeout=300.0,  # 5 minutes
)
```

### Reconnection Behavior

The SSE client automatically reconnects with exponential backoff:

1. First reconnect: `reconnect_delay` (e.g., 1 second)
2. Second reconnect: `reconnect_delay * 1.5` (e.g., 1.5 seconds)
3. Continues until `max_reconnect_delay` is reached

## Configuration Profiles

### Development

```python
client = CGPClient(
    api_key="sk_test_...",
    endpoint="http://localhost:8000",
    debug=True,
    fail_silently=False,  # See errors during development
    flush_interval=1.0,   # Faster feedback for testing
)
```

### Production

```python
client = CGPClient(
    api_key="sk_live_...",
    endpoint="https://api.steward-agent.com",
    debug=False,
    fail_silently=True,   # Don't crash on SDK errors
    flush_interval=5.0,
    max_retries=5,        # More resilient
)
```

### High-Throughput

```python
client = CGPClient(
    batch_size=500,           # Larger batches
    flush_interval=10.0,      # Less frequent flushes
    max_queue_size=50000,     # Larger queue
)
```

## Disabling the SDK

### Globally via Environment

```bash
CGP_ENABLED=false
```

### Programmatically

```python
client = CGPClient(enabled=False)
```

When disabled:
- Traces are silently discarded
- No network requests are made
- All methods return safely (no errors)

This is useful for:
- Local development without backend
- Disabling in certain environments
- A/B testing SDK impact

## Validating Configuration

```python
# Check if SDK is properly configured
if client.config.is_configured():
    print("SDK is ready")
else:
    print("Missing API key or endpoint")

# Get current configuration
print(f"Endpoint: {client.config.endpoint}")
print(f"API Version: {client.config.api_version}")
print(f"Batch Size: {client.config.batch_size}")
```

## Using .env Files

The SDK automatically loads `.env` files via `python-dotenv`:

```bash
# .env
CGP_API_KEY=sk_live_xxxxxxxx
CGP_ENDPOINT=https://api.steward-agent.com
CGP_DEBUG=true
```

```python
# Automatically loaded when importing cgp_sdk
from cgp_sdk import CGPClient

client = CGPClient()  # Uses values from .env
```

## Security Notes

1. **Never commit API keys** - Use environment variables or secret managers
2. **Use `sk_test_` keys** for development/testing
3. **Use `sk_live_` keys** only in production
4. **Rotate keys** if they may have been exposed
