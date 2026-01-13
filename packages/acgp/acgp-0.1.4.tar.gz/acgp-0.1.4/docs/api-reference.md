# API Reference

Complete reference for all CGP SDK classes and methods.

## CGPClient

The main client class for interacting with the Steward Agent backend.

### Constructor

```python
CGPClient(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    on_feedback: Optional[Callable[[str, Dict], None]] = None,
    on_flush_complete: Optional[Callable[[List[BatchResult]], None]] = None,
    sse_config: Optional[SSEConfig] = None,
    **config_kwargs
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | `CGP_API_KEY` env | API key for authentication |
| `endpoint` | `str` | `CGP_ENDPOINT` env | Backend API endpoint URL |
| `on_feedback` | `Callable` | `None` | Callback for real-time SSE feedback |
| `on_flush_complete` | `Callable` | `None` | Callback after each batch flush |
| `sse_config` | `SSEConfig` | `None` | SSE streaming configuration |
| `debug` | `bool` | `False` | Enable debug logging |
| `enabled` | `bool` | `True` | Master switch to enable/disable SDK |
| `fail_silently` | `bool` | `True` | Suppress exceptions (log instead) |

### Methods

#### trace()

Create a trace context manager for capturing agent execution.

```python
trace(
    agent_type: str,
    goal: str,
    agent_tag: Optional[str] = None,
    user_query: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> TraceContext
```

**Parameters:**
- `agent_type`: Type of agent (`"planner"`, `"executor"`, `"unified"`, or custom)
- `goal`: What the agent is trying to accomplish
- `agent_tag`: **Recommended.** Unique identifier for this agent (e.g., `"inventory-planner"`, `"crm-executor"`). Defaults to `"A"` for planner, `"B"` for executor if not provided. See [Agent Tagging](#agent-tagging) for best practices.
- `user_query`: Original user query (defaults to goal)
- `metadata`: Additional metadata to include

**Returns:** `TraceContext` for use in a `with` statement

**Example:**
```python
with client.trace(
    agent_type="planner",
    agent_tag="research-planner",  # Unique identifier
    goal="Plan the research"
) as trace:
    result = agent.run()
    trace.set_output(result)
```

---

#### capture_trace()

Manually capture a trace without using a context manager.

```python
capture_trace(
    agent_type: str,
    goal: str,
    reasoning_text: str = "",
    final_output: str = "",
    agent_tag: Optional[str] = None,
    user_query: Optional[str] = None,
    output_type: Optional[str] = None,
    context_information: Optional[Dict[str, Any]] = None,
    documents_used: Optional[List[str]] = None,
    similarity_scores: Optional[List[float]] = None,
) -> str
```

**Returns:** `trace_id` string

**Example:**
```python
trace_id = client.capture_trace(
    agent_type="executor",
    agent_tag="order-executor",  # Unique identifier
    goal="Execute the plan",
    reasoning_text="Processed input and generated output",
    final_output="Here is the result...",
)
```

---

#### flush()

Force-send all pending traces immediately.

```python
flush() -> List[BatchResult]
```

**Returns:** List of `BatchResult` objects from the flush operation

**Example:**
```python
results = client.flush()
print(f"Sent {len(results)} batches")
```

---

#### wait_for_feedback()

Wait for all pending traces to receive feedback via SSE.

```python
wait_for_feedback(
    timeout: Optional[float] = None,
    auto_flush: bool = True,
) -> bool
```

**Parameters:**
- `timeout`: Maximum seconds to wait (`None` = wait forever)
- `auto_flush`: If `True` (default), flushes pending traces before waiting

**Returns:** `True` if all feedback received, `False` if timeout

**Example:**
```python
if client.wait_for_feedback(timeout=30.0):
    print("All feedback received!")
else:
    print("Timeout - some feedback pending")
```

---

#### get_score()

Get CTQ scores for a trace with automatic retry.

```python
get_score(
    trace_id: str,
    wait_for_processing: bool = True,
    max_attempts: int = 5,
    initial_delay: float = 1.0,
) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `trace_id`: The trace identifier
- `wait_for_processing`: If `True`, retries until trace is processed
- `max_attempts`: Maximum retry attempts
- `initial_delay`: Initial delay between retries (uses exponential backoff)

**Returns:** CTQ score data or `None`

**Example:**
```python
score = client.get_score(trace_id)
if score and score.get('scores'):
    print(f"Composite: {score['scores'].get('composite_score')}")
```

---

#### get_feedback()

Get oversight feedback for a trace with automatic retry.

```python
get_feedback(
    trace_id: str,
    wait_for_processing: bool = True,
    max_attempts: int = 5,
    initial_delay: float = 1.0,
) -> Optional[Dict[str, Any]]
```

**Returns:** Feedback data or `None`

---

#### get_metrics()

Get SDK metrics including queue and SSE statistics.

```python
get_metrics() -> Dict[str, Any]
```

**Returns:** Dictionary with metrics

**Example:**
```python
metrics = client.get_metrics()
print(f"SSE Connected: {metrics['sse_connected']}")
print(f"Pending: {metrics['pending_feedback']}")
```

---

#### close()

Close the client and release resources.

```python
close(timeout: Optional[float] = None) -> None
```

**Parameters:**
- `timeout`: Max seconds to wait for flush (default: 10s)

---

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `sse_connected` | `bool` | Whether SSE stream is connected |
| `pending_feedback_count` | `int` | Number of traces waiting for feedback |

---

## TraceContext

Context manager for capturing agent execution traces.

### Methods

#### set_output()

Set the agent's final output.

```python
set_output(output: str, output_type: Optional[str] = None) -> TraceContext
```

**Example:**
```python
trace.set_output("The analysis shows...", output_type="analysis")
```

---

#### set_reasoning()

Set the agent's reasoning/thought process.

```python
set_reasoning(reasoning: str) -> TraceContext
```

**Example:**
```python
trace.set_reasoning("Step 1: Parsed input. Step 2: Analyzed data...")
```

---

#### add_context()

Add context information to the trace.

```python
add_context(key: str, value: Any) -> TraceContext
```

**Example:**
```python
trace.add_context("model", "gpt-4")
trace.add_context("temperature", 0.7)
```

---

#### set_documents()

Set documents used by the agent (for RAG).

```python
set_documents(
    documents: List[str],
    similarity_scores: Optional[List[float]] = None,
) -> TraceContext
```

**Example:**
```python
trace.set_documents(
    documents=["doc1.pdf", "doc2.pdf"],
    similarity_scores=[0.95, 0.87]
)
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `trace_id` | `str` | Unique identifier for this trace |

---

## SSEConfig

Configuration for SSE streaming.

```python
SSEConfig(
    reconnect_delay: float = 1.0,      # Initial reconnect delay (seconds)
    max_reconnect_delay: float = 30.0, # Maximum reconnect delay
    connection_timeout: float = 10.0,  # Connection timeout
    read_timeout: float = 300.0,       # Read timeout (5 minutes)
)
```

---

## cgp_trace Decorator

Decorator for automatically tracing function-based agents.

```python
@cgp_trace(
    client: CGPClient,
    agent_type: str,
    agent_tag: Optional[str] = None,
    goal: Optional[str] = None,
    extract_output: bool = True,
)
def my_agent_function(query: str) -> str:
    ...
```

**Parameters:**
- `client`: CGPClient instance
- `agent_type`: Type of agent
- `agent_tag`: **Recommended.** Unique identifier for this agent. See [Agent Tagging](#agent-tagging).
- `goal`: Optional fixed goal (defaults to first argument)
- `extract_output`: Whether to capture return value as output

**Example:**
```python
@cgp_trace(client, agent_type="planner", agent_tag="myapp-planner")
def plan(query: str) -> str:
    return generate_plan(query)

result = plan("What should we do?")  # Automatically traced
```

---

## Type Aliases

```python
FeedbackCallback = Callable[[str, Dict[str, Any]], None]
```

Signature for the `on_feedback` callback:
- First argument: `trace_id` (str)
- Second argument: `feedback_data` (dict) containing:
  - `ctq_scores`: CTQ score breakdown
  - `feedback`: Feedback text
  - `requires_hitl`: Whether human review is needed
  - `oversight_mode`: Current oversight mode

---

## Agent Tagging

The `agent_tag` parameter uniquely identifies each agent in your dashboard. While it defaults to `"A"` for planners and `"B"` for executors, **providing unique tags is strongly recommended**.

### Why Unique Tags Matter

Without unique tags, agents from different applications using the same API key will be indistinguishable:

| App | Agent Type | Default Tag | Result |
|-----|-----------|-------------|--------|
| E-commerce | planner | A | Both show as "Agent A" |
| Support Bot | planner | A | Cannot differentiate |

With unique tags:

| App | Agent Type | Custom Tag | Result |
|-----|-----------|------------|--------|
| E-commerce | planner | ecommerce-planner | Clearly identified |
| Support Bot | planner | support-planner | Clearly identified |

### Naming Conventions

Recommended formats:
- `{app-name}-{role}`: `inventory-planner`, `crm-executor`
- `{app-name}/{role}`: `inventory/planner`, `crm/executor`
- `{team}-{app}-{role}`: `sales-crm-lead-scorer`

### Examples

```python
# Single app with multiple agents
with client.trace(agent_type="planner", agent_tag="order-planner", goal="...") as trace: ...
with client.trace(agent_type="executor", agent_tag="order-executor", goal="...") as trace: ...
with client.trace(agent_type="executor", agent_tag="notification-sender", goal="...") as trace: ...

# Multiple apps sharing same API key
# App 1: E-commerce
with client.trace(agent_type="planner", agent_tag="ecommerce-order-planner", goal="...") as trace: ...

# App 2: Customer Support
with client.trace(agent_type="planner", agent_tag="support-ticket-analyzer", goal="...") as trace: ...
```
