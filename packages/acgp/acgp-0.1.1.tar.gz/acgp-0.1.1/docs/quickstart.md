# Quick Start Guide

Get up and running with CGP SDK in 5 minutes.

## Prerequisites

- Python 3.9+
- A Steward Agent API key
- Your agent code (any framework)

## Step 1: Install the SDK

```bash
pip install cgp-sdk
```

## Step 2: Set Up Environment Variables

Create a `.env` file or set environment variables:

```bash
CGP_API_KEY=sk_live_your_api_key_here
CGP_ENDPOINT=https://api.steward-agent.com
```

## Step 3: Add Tracing to Your Agent

### Option A: Real-time Feedback (Recommended)

```python
from cgp_sdk import CGPClient

# 1. Define a callback to receive feedback
def handle_feedback(trace_id: str, feedback_data: dict):
    ctq = feedback_data.get('ctq_scores', {})
    print(f"[Feedback] Trace {trace_id[:8]}...")
    print(f"  Score: {ctq.get('composite_score', 'N/A')}")

    if feedback_data.get('requires_hitl'):
        print("  ALERT: Human review required!")

# 2. Create client with callback
client = CGPClient(
    on_feedback=handle_feedback,  # Enables SSE streaming
)

# 3. Wrap your agent execution
with client.trace(agent_type="planner", goal="Analyze the user query") as trace:
    # Your agent code here
    result = my_agent.run(user_query)

    # Capture the output
    trace.set_output(result)
    trace.set_reasoning("Analyzed query and generated plan")

# 4. Wait for feedback and cleanup
client.wait_for_feedback(timeout=30.0)
client.close()
```

### Option B: Manual Polling

```python
from cgp_sdk import CGPClient

client = CGPClient()

with client.trace(agent_type="executor", goal="Execute the plan") as trace:
    result = my_agent.execute(plan)
    trace.set_output(result)

# Manually flush and retrieve results
client.flush()
score = client.get_score(trace.trace_id)
feedback = client.get_feedback(trace.trace_id)

print(f"Score: {score}")
print(f"Feedback: {feedback}")

client.close()
```

## Step 4: View Results in Dashboard

Visit your Steward Agent dashboard to see:
- Trace history with CTQ scores
- Detailed feedback and recommendations
- Trends and analytics

## Next Steps

- [API Reference](api-reference.md) - Explore all available methods
- [Configuration](configuration.md) - Customize SDK behavior
- [Framework Integration](frameworks.md) - Integrate with CrewAI, LangChain, etc.

## Common Issues

### "SSE Connected: False"
The SSE connection happens in a background thread. Give it 1-2 seconds to connect, or check for network/authentication issues.

### Timeout waiting for feedback
The backend may be processing large traces. Increase the timeout or check backend logs.

### No feedback received
Ensure your API key is valid and has the correct permissions. Check that traces are being sent (`client.flush()`).

See [Troubleshooting](troubleshooting.md) for more solutions.
