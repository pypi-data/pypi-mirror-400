# CGP SDK Implementation Plan
# Cognitive Governance Protocol - Python SDK

## Overview

Lightweight Python SDK for integrating Steward Agent oversight into any AI agent pipeline.

**Architecture Flow:**
```
Client Code -> CGP SDK (lightweight wrapper) -> Steward API -> Backend Infrastructure
```

**Key Principles:**
- Framework-agnostic (works with any Python agent)
- Tiny footprint (~1.5MB dependencies)
- Async by default - never blocks client agent execution
- Graceful degradation - works offline, queues events locally
- Batching - accumulates events, flushes at thresholds

---

## Repository Structure

```
cgp-sdk/
├── cgp_sdk/
│   ├── __init__.py              # Public API exports
│   ├── client.py                # CGPClient - main entry point
│   ├── config.py                # SDK configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trace.py             # AgentReasoningTrace (simplified)
│   │   ├── score.py             # CTQScore response model
│   │   └── feedback.py          # SocraticNudge, HITLAlert models
│   ├── transport/
│   │   ├── __init__.py
│   │   ├── async_queue.py       # Local event queue + background flusher
│   │   ├── batch_sender.py      # Batched HTTP transport
│   │   └── retry.py             # Retry logic with exponential backoff
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py              # BaseAdapter protocol
│   │   ├── crewai.py            # CrewAI adapter
│   │   ├── langchain.py         # LangChain adapter
│   │   └── generic.py           # Generic Python callable adapter
│   ├── wrapper/
│   │   ├── __init__.py
│   │   ├── agent_protocol.py    # MonitorableAgent protocol
│   │   ├── agent_wrapper.py     # Universal wrapper
│   │   └── decorator.py         # @cgp_trace decorator
│   └── utils/
│       ├── __init__.py
│       ├── context.py           # Context manager for tracing
│       └── observer_interface.py # Observer pattern interfaces
├── examples/
│   ├── quickstart.py
│   ├── crewai_integration.py
│   ├── langchain_integration.py
│   └── custom_agent.py
├── tests/
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

---

## What to Extract from steward-agent-gov-backend

### Files to COPY (Already Written - 2,850 lines)

| Source File | Target Location | Lines | Status |
|-------------|-----------------|-------|--------|
| `src/wrapper/agent_protocol.py` | `cgp_sdk/wrapper/agent_protocol.py` | 365 | Ready |
| `src/wrapper/steward_agent_wrapper.py` | `cgp_sdk/wrapper/agent_wrapper.py` | 531 | Ready |
| `src/wrapper/steward_decorator.py` | `cgp_sdk/wrapper/decorator.py` | 354 | Ready |
| `src/adapters/generic_adapter.py` | `cgp_sdk/adapters/generic.py` | 407 | Ready |
| `src/adapters/crewai_adapter.py` | `cgp_sdk/adapters/crewai.py` | 400 | Ready |
| `src/utils/data_models.py` | `cgp_sdk/models/data_models.py` | 535 | Ready |
| `src/utils/observer_interface.py` | `cgp_sdk/utils/observer_interface.py` | 262 | Ready |

### Files to CREATE (New - ~950 lines)

| File | Purpose | Est. Lines |
|------|---------|------------|
| `cgp_sdk/__init__.py` | Public API exports | 50 |
| `cgp_sdk/client.py` | CGPClient main class | 300 |
| `cgp_sdk/config.py` | SDK configuration | 100 |
| `cgp_sdk/transport/async_queue.py` | Background event queue | 200 |
| `cgp_sdk/transport/batch_sender.py` | HTTP batching | 150 |
| `cgp_sdk/transport/retry.py` | Retry with backoff | 100 |
| `pyproject.toml` | Package config | 50 |

---

## Public API Design

```python
from cgp_sdk import CGPClient, cgp_trace

# Initialize once
client = CGPClient(
    api_key="sk_...",
    endpoint="https://api.steward-agent.com",  # or self-hosted
    flush_interval=5.0,      # seconds
    batch_size=100,          # events per batch
    max_queue_size=10000,    # local buffer limit
)

# Option 1: Decorator
@cgp_trace(client, agent_type="planner")
def my_agent_function(query: str) -> str:
    # Agent logic here
    return result

# Option 2: Context manager
with client.trace(agent_type="executor", goal="Process query") as trace:
    result = my_agent.run(query)
    trace.set_output(result)
    trace.set_reasoning(my_agent.reasoning_log)

# Option 3: Manual
trace_id = client.capture_trace(
    agent_type="planner",
    goal="Analyze user request",
    reasoning_text="Step 1: Parse input...",
    final_output="Plan: ...",
)

# Query results (sync call when needed)
score = client.get_score(trace_id)
feedback = client.get_feedback(trace_id)

# Graceful shutdown
client.flush()
client.close()
```

---

## Dependencies

### Core (Required - ~1.5MB)
```
pydantic>=2.0.0
httpx>=0.25.0
python-dotenv>=1.0.0
pyyaml>=6.0
```

### Optional Extras
```
# pip install cgp-sdk[anthropic]
anthropic>=0.17.0

# pip install cgp-sdk[crewai]
crewai>=0.28.0

# pip install cgp-sdk[langchain]
langchain>=0.1.0
```

---

## Implementation Phases

### Phase 1: SDK Extraction (3-4 days)
- [ ] Create repo structure
- [ ] Copy wrapper/, adapters/, utils/ modules
- [ ] Create pyproject.toml with minimal deps
- [ ] Write CGPClient with sync API calls (no batching yet)
- [ ] Write basic quickstart example
- [ ] Test: SDK can send traces to existing backend

### Phase 2: Async Transport (2-3 days)
- [ ] Implement AsyncEventQueue (background thread)
- [ ] Implement BatchSender (accumulate, flush)
- [ ] Add retry logic with exponential backoff
- [ ] Add graceful degradation (offline queuing)
- [ ] Test: SDK batches events, handles failures

### Phase 3: Polish & Publish (2-3 days)
- [ ] SDK documentation
- [ ] Comprehensive examples
- [ ] PyPI package publishing
- [ ] Integration tests

---

## Transport Layer Architecture

```python
class AsyncEventQueue:
    """Thread-safe queue with background flusher"""
    - In-memory queue with max size
    - Background thread flushes periodically
    - Falls back to disk queue if memory full
    - Exponential backoff on failures

class BatchSender:
    """HTTP transport with batching"""
    - Accumulates events until threshold
    - Compresses payload (gzip)
    - Retries with idempotency keys
    - Circuit breaker for backend failures
```

---

## Success Criteria

1. Client can install SDK with `pip install cgp-sdk`
2. Integration requires <20 lines of code change
3. SDK adds <5ms latency to agent execution (async)
4. Works offline - queues events locally
5. Graceful degradation - never crashes client code
