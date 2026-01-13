# Best Practices

Production recommendations for using CGP SDK effectively.

## Initialization

### Use Context Managers

Always use the client as a context manager or call `close()` explicitly:

```python
# Recommended: Context manager
with CGPClient(api_key="sk_...") as client:
    with client.trace(...) as trace:
        result = agent.run()
        trace.set_output(result)
    client.wait_for_feedback(timeout=30)

# Alternative: Explicit close
client = CGPClient(api_key="sk_...")
try:
    # ... your code ...
finally:
    client.close()
```

### Initialize Once, Reuse

Create one client instance and reuse it:

```python
# Good: Single instance
client = CGPClient(api_key="sk_...", on_feedback=handle_feedback)

for query in queries:
    with client.trace(...) as trace:
        result = agent.run(query)
        trace.set_output(result)

client.wait_for_feedback(timeout=60)
client.close()

# Bad: New client per request (inefficient)
for query in queries:
    client = CGPClient(api_key="sk_...")  # Don't do this!
    with client.trace(...) as trace:
        ...
    client.close()
```

## Tracing

### Always Set Output

Every trace should have output set:

```python
with client.trace(agent_type="executor", goal="Process data") as trace:
    try:
        result = agent.run()
        trace.set_output(result)  # Always set output
    except Exception as e:
        trace.set_output(f"Error: {str(e)}")  # Even on errors
        raise
```

### Include Reasoning

Reasoning helps the oversight system provide better feedback:

```python
trace.set_reasoning("""
Step 1: Parsed the user query to identify intent
Step 2: Retrieved relevant documents from knowledge base
Step 3: Generated response based on retrieved context
""")
```

### Use Meaningful Goals

Goals should describe what the agent is trying to accomplish:

```python
# Good: Specific, actionable goals
trace = client.trace(
    agent_type="planner",
    goal="Create a 3-step plan to analyze customer feedback data"
)

# Bad: Vague goals
trace = client.trace(
    agent_type="planner",
    goal="Do stuff"  # Not helpful
)
```

### Use Unique Agent Tags

Provide unique `agent_tag` values to distinguish agents across applications:

```python
# Good: Unique, descriptive tags
with client.trace(
    agent_type="planner",
    agent_tag="inventory-order-planner",  # Unique identifier
    goal="Plan inventory update"
) as trace:
    result = planner.run()
    trace.set_output(result)

# Bad: Using defaults (leads to collisions)
with client.trace(
    agent_type="planner",
    goal="Plan inventory update"
    # agent_tag defaults to "A" - will collide with other apps!
) as trace:
    ...
```

**Why this matters:**
- Multiple apps using the same API key will have agents with tag "A" or "B"
- Dashboard cannot distinguish between them
- Analytics and filtering become unreliable

**Naming conventions:**
- `{app-name}-{role}`: `inventory-planner`, `crm-executor`
- `{team}-{app}-{role}`: `sales-crm-lead-scorer`

### Add Relevant Context

Include metadata that helps understand the trace:

```python
trace.add_context("model", "gpt-4")
trace.add_context("temperature", 0.7)
trace.add_context("user_id", user_id)  # For debugging
trace.add_context("session_id", session_id)
trace.add_context("tools_available", ["search", "calculator", "code_exec"])
```

## Error Handling

### Use fail_silently for Production

```python
# Production: Don't let SDK errors crash your app
client = CGPClient(
    api_key="sk_...",
    fail_silently=True,  # Default
)

# Development: See all errors
client = CGPClient(
    api_key="sk_...",
    fail_silently=False,
)
```

### Handle Callback Errors

Errors in callbacks shouldn't crash your application:

```python
def handle_feedback(trace_id, data):
    try:
        score = data.get('ctq_scores', {}).get('composite_score')
        if score and score < 0.5:
            alert_low_quality(trace_id, score)
    except Exception as e:
        logging.error(f"Feedback handler error: {e}")
        # Don't re-raise - let the SDK continue
```

## Performance

### Batch Appropriately

```python
# High-throughput scenarios
client = CGPClient(
    batch_size=500,        # Larger batches = fewer requests
    flush_interval=10.0,   # Less frequent flushes
)

# Low-latency scenarios
client = CGPClient(
    batch_size=10,         # Smaller batches = faster feedback
    flush_interval=1.0,    # More frequent flushes
)
```

### Don't Block on Feedback

Use callbacks for real-time feedback instead of blocking:

```python
# Good: Non-blocking with callback
def handle_feedback(trace_id, data):
    # Process feedback asynchronously
    log_feedback(trace_id, data)

client = CGPClient(on_feedback=handle_feedback)

# Process many requests without blocking
for query in queries:
    with client.trace(...) as trace:
        result = agent.run(query)
        trace.set_output(result)
    # Don't wait here - callback handles it

# Only wait at the end
client.wait_for_feedback(timeout=60)

# Bad: Blocking per request
for query in queries:
    with client.trace(...) as trace:
        result = agent.run(query)
        trace.set_output(result)
    client.flush()
    score = client.get_score(trace.trace_id)  # Blocks!
```

### Limit Output Size

Large outputs slow down processing:

```python
# Truncate very large outputs
MAX_OUTPUT_SIZE = 50000  # 50KB

output = agent.run()
if len(output) > MAX_OUTPUT_SIZE:
    output = output[:MAX_OUTPUT_SIZE] + "\n[TRUNCATED]"

trace.set_output(output)
```

## Security

### Protect API Keys

```python
# Good: Environment variables
client = CGPClient()  # Reads from CGP_API_KEY

# Good: Secret manager
from my_secrets import get_secret
client = CGPClient(api_key=get_secret("cgp_api_key"))

# Bad: Hardcoded keys
client = CGPClient(api_key="sk_live_abc123")  # Never do this!
```

### Sanitize Sensitive Data

Don't include sensitive information in traces:

```python
def sanitize(text):
    # Remove PII, credentials, etc.
    text = re.sub(r'\b\d{16}\b', '[CARD_NUMBER]', text)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    return text

with client.trace(...) as trace:
    result = agent.run(query)
    trace.set_output(sanitize(result))
    trace.set_reasoning(sanitize(agent.reasoning))
```

## Monitoring

### Log SDK Metrics

```python
import logging

def log_metrics():
    metrics = client.get_metrics()
    logging.info(f"CGP SDK Metrics: {metrics}")

# Periodic logging
import threading
def metrics_logger():
    while True:
        log_metrics()
        time.sleep(60)

threading.Thread(target=metrics_logger, daemon=True).start()
```

### Monitor SSE Connection

```python
def on_feedback(trace_id, data):
    # Your feedback handling
    pass

def on_error(error):
    logging.error(f"SSE error: {error}")
    alert_ops_team(error)

client = CGPClient(
    on_feedback=on_feedback,
    # SSE client logs warnings on reconnection
)

# Check connection status
if not client.sse_connected:
    logging.warning("SSE not connected - feedback may be delayed")
```

## Testing

### Mock for Unit Tests

```python
from unittest.mock import MagicMock, patch

def test_my_agent():
    # Mock the CGPClient
    mock_client = MagicMock()
    mock_trace = MagicMock()
    mock_client.trace.return_value.__enter__ = lambda s: mock_trace
    mock_client.trace.return_value.__exit__ = lambda s, *args: None

    with patch('my_module.CGPClient', return_value=mock_client):
        result = my_function()

    # Verify trace was set
    mock_trace.set_output.assert_called_once()
```

### Disable for CI/CD

```bash
# In CI environment
CGP_ENABLED=false pytest
```

```python
# Or programmatically
import os
if os.getenv("CI"):
    client = CGPClient(enabled=False)
```

## Graceful Shutdown

### Wait for Pending Work

```python
import signal
import sys

client = CGPClient(on_feedback=handle_feedback)

def shutdown_handler(signum, frame):
    print("Shutting down...")

    # Wait for pending feedback
    client.wait_for_feedback(timeout=10)

    # Close client
    client.close()

    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

### In Web Applications

```python
# FastAPI
from fastapi import FastAPI
from contextlib import asynccontextmanager

client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = CGPClient(on_feedback=handle_feedback)
    yield
    client.wait_for_feedback(timeout=10)
    client.close()

app = FastAPI(lifespan=lifespan)
```
