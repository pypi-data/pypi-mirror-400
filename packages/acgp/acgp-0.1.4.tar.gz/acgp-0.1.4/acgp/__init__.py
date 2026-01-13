"""
ACGP SDK - Agentic Cognitive Governance Protocol
Lightweight Python SDK for AI agent oversight integration.

Basic Usage (Real-time Feedback - Recommended):

    from acgp import ACGPClient

    def handle_feedback(trace_id: str, feedback_data: dict):
        print(f"Feedback for {trace_id}: {feedback_data}")

    client = ACGPClient(
        api_key="sk_...",
        on_feedback=handle_feedback  # Real-time SSE streaming
    )

    with client.trace(agent_type="planner", goal="Analyze query") as trace:
        result = my_agent.run(query)
        trace.set_output(result)
    # Feedback callback fires automatically!

    client.wait_for_feedback(timeout=30)  # Optional: wait before shutdown
    client.close()


Alternative Usage (Manual Polling):

    from acgp import ACGPClient, acgp_trace

    client = ACGPClient(api_key="sk_...")

    # Option 1: Decorator
    @acgp_trace(client, agent_type="planner")
    def my_agent(query):
        return process(query)

    # Option 2: Context manager
    with client.trace(agent_type="executor", goal="Process query") as trace:
        result = my_agent.run(query)
        trace.set_output(result)

    # Option 3: Manual capture
    trace_id = client.capture_trace(
        agent_type="planner",
        goal="Analyze request",
        final_output="Result..."
    )

    # Flush and poll for results
    client.flush()
    score = client.get_score(trace_id)
    feedback = client.get_feedback(trace_id)
"""

__version__ = "0.1.4"

from .client import ACGPClient, acgp_trace, TraceContext, FeedbackCallback
from .config import ACGPConfig, load_config
from .transport import BatchResult, QueueConfig, BatchConfig, RetryConfig, SSEConfig

__all__ = [
    "__version__",
    "ACGPClient",
    "acgp_trace",
    "TraceContext",
    "FeedbackCallback",
    "ACGPConfig",
    "load_config",
    # Transport (for advanced users)
    "BatchResult",
    "QueueConfig",
    "BatchConfig",
    "RetryConfig",
    "SSEConfig",
]
