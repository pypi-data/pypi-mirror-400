# CGP SDK Documentation

Welcome to the CGP SDK documentation. This SDK provides a lightweight way to integrate AI agent oversight into any Python agent pipeline.

## What is CGP SDK?

The **Cognitive Governance Protocol (CGP) SDK** connects your AI agents to the Steward Agent backend for real-time quality monitoring and oversight. It captures agent execution traces, sends them for analysis, and delivers feedback via SSE streaming.

## Key Concepts

### Traces
A **trace** captures a single agent execution, including:
- **Goal**: What the agent was trying to accomplish
- **Output**: The agent's response/result
- **Reasoning**: The agent's thought process
- **Context**: Additional metadata (model, documents used, etc.)

### CTQ Scores
**Critical-to-Quality (CTQ) scores** measure trace quality:
- `composite_score`: Overall quality (0.0 - 1.0)
- `goal_coherence`: How well output aligns with goal
- `context_consistency`: Consistency with provided context
- `information_completeness`: Coverage of required information

### Feedback
**Oversight feedback** includes:
- Socratic nudges for improvement
- HITL (Human-in-the-Loop) alerts when human review is needed
- Specific recommendations based on active blueprints

## Documentation Sections

- [Quick Start](quickstart.md) - Get up and running in 5 minutes
- [API Reference](api-reference.md) - Complete API documentation
- [Configuration](configuration.md) - Environment variables and options
- [Framework Integration](frameworks.md) - CrewAI, LangChain, and more
- [Best Practices](best-practices.md) - Production recommendations
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## Installation

```bash
pip install cgp-sdk
```

## Minimal Example

```python
from cgp_sdk import CGPClient

def handle_feedback(trace_id, data):
    print(f"Score: {data.get('ctq_scores', {}).get('composite_score')}")

client = CGPClient(
    api_key="sk_live_...",
    endpoint="https://api.steward-agent.com",
    on_feedback=handle_feedback,
)

with client.trace(agent_type="planner", goal="Analyze query") as trace:
    result = my_agent.run(query)
    trace.set_output(result)

client.wait_for_feedback(timeout=30)
client.close()
```

## Support

- GitHub Issues: https://github.com/steward-ai/cgp-sdk/issues
- Email: support@steward-agent.com
