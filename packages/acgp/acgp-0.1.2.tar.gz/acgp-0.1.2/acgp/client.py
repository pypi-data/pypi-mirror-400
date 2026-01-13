"""
ACGP SDK Client

Main client class for the Agentic Cognitive Governance Protocol SDK.
Provides a simple interface for capturing agent traces and retrieving oversight feedback.
"""

import uuid
import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from contextlib import contextmanager
from functools import wraps

import httpx

from .config import ACGPConfig, load_config
from .transport import (
    AsyncEventQueue,
    QueueConfig,
    BatchConfig,
    BatchResult,
    RetryConfig,
    SSEClient,
    SSEConfig,
)


logger = logging.getLogger("acgp")


# Type alias for feedback callback
FeedbackCallback = Callable[[str, Dict[str, Any]], None]


class TraceContext:
    """
    Context manager for capturing agent execution traces.

    Usage:
        with client.trace(
            agent_type="planner",
            agent_tag="myapp-query-planner",  # Recommended: unique identifier
            goal="Analyze query"
        ) as trace:
            result = my_agent.run(query)
            trace.set_output(result)
            trace.set_reasoning("Step 1: parsed input...")

    Note:
        It is recommended to provide a unique `agent_tag` for each agent to
        distinguish them in the dashboard. Without a unique tag, agents from
        different apps using the same API key will appear as "A" or "B",
        making them indistinguishable.

        Good tag examples: "inventory-planner", "crm-executor", "support-analyzer"
    """

    def __init__(
        self,
        client: "ACGPClient",
        agent_type: str,
        goal: str,
        agent_tag: Optional[str] = None,
        user_query: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.client = client
        self.trace_id = str(uuid.uuid4())
        self.agent_type = agent_type
        self.agent_tag = agent_tag or self._infer_tag(agent_type)
        self.goal = goal
        self.user_query = user_query or goal
        self.metadata = metadata or {}

        self._reasoning_text: Optional[str] = None
        self._final_output: Optional[str] = None
        self._output_type: Optional[str] = None
        self._context_info: Dict[str, Any] = {}
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

    def _infer_tag(self, agent_type: str) -> str:
        """Infer agent tag from type."""
        return "A" if agent_type.lower() == "planner" else "B"

    def set_reasoning(self, reasoning: str) -> "TraceContext":
        """Set the agent's reasoning text."""
        self._reasoning_text = reasoning
        return self

    def set_output(self, output: str, output_type: Optional[str] = None) -> "TraceContext":
        """Set the agent's final output."""
        self._final_output = output
        self._output_type = output_type
        return self

    def add_context(self, key: str, value: Any) -> "TraceContext":
        """Add context information to the trace."""
        self._context_info[key] = value
        return self

    def set_documents(self, documents: List[str], similarity_scores: Optional[List[float]] = None) -> "TraceContext":
        """Set documents used by the agent."""
        self._context_info["documents_used"] = documents
        if similarity_scores:
            self._context_info["similarity_scores"] = similarity_scores
        return self

    def __enter__(self) -> "TraceContext":
        self._start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end_time = datetime.now()

        # Build trace data
        trace_data = {
            "trace_id": self.trace_id,
            "agent_type": self.agent_type,
            "agent_tag": self.agent_tag,
            "goal": self.goal,
            "user_query": self.user_query,
            "reasoning_text": self._reasoning_text or "",
            "final_output": self._final_output or "",
            "output_type": self._output_type,
            "context_information": {**self._context_info, **self.metadata},
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "had_error": exc_type is not None,
        }

        # Send trace (non-blocking in future with async transport)
        self.client._send_trace(trace_data)

        # Don't suppress exceptions
        return False


class ACGPClient:
    """
    Main client for the Agentic Cognitive Governance Protocol SDK.

    Provides methods for capturing agent traces, retrieving CTQ scores,
    and getting oversight feedback from the Steward Agent backend.

    Usage Patterns:

        # Pattern 1: Real-time feedback via callback (RECOMMENDED)
        # Feedback arrives automatically via SSE stream as traces are processed

        def handle_feedback(trace_id: str, feedback_data: dict):
            print(f"Feedback for {trace_id}:")
            print(f"  Score: {feedback_data.get('ctq_scores')}")
            print(f"  Feedback: {feedback_data.get('feedback')}")

        client = ACGPClient(
            api_key="sk_...",
            on_feedback=handle_feedback  # Enables real-time SSE streaming
        )

        with client.trace(agent_type="planner", goal="Analyze query") as trace:
            result = my_agent.run(query)
            trace.set_output(result)
        # Feedback callback fires automatically when processing completes!

        # Optional: wait for all pending feedback before shutdown
        client.wait_for_feedback(timeout=30.0)
        client.close()


        # Pattern 2: Manual polling (legacy)
        # Flush traces and manually query for results

        client = ACGPClient(api_key="sk_...")

        with client.trace(agent_type="planner", goal="Analyze query") as trace:
            result = my_agent.run(query)
            trace.set_output(result)

        trace_id = trace.trace_id
        client.flush()  # Force send pending traces

        # Poll for results
        score = client.get_score(trace_id)
        feedback = client.get_feedback(trace_id)
        client.close()
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        on_flush_complete: Optional[Callable[[List[BatchResult]], None]] = None,
        on_feedback: Optional[FeedbackCallback] = None,
        sse_config: Optional[SSEConfig] = None,
        **config_kwargs
    ):
        """
        Initialize the CGP client.

        Args:
            api_key: API key for authentication (or set CGP_API_KEY env var)
            endpoint: Backend API endpoint (or set CGP_ENDPOINT env var)
            on_flush_complete: Optional callback after each batch flush
            on_feedback: Optional callback for real-time feedback via SSE.
                         Signature: (trace_id: str, feedback_data: dict) -> None
                         When provided, SSE streaming is automatically enabled.
            sse_config: Optional SSE configuration (reconnect delays, timeouts)
            **config_kwargs: Additional configuration options
        """
        self.config = load_config(api_key=api_key, endpoint=endpoint, **config_kwargs)

        # HTTP client with connection pooling
        self._http_client: Optional[httpx.Client] = None
        self._http_lock = threading.Lock()
        self._queue_lock = threading.Lock()

        # Async event queue for non-blocking trace sending
        self._event_queue: Optional[AsyncEventQueue] = None
        self._queue_started = False
        self._on_flush_complete = on_flush_complete

        # SSE client for real-time feedback streaming
        self._on_feedback = on_feedback
        self._sse_client: Optional[SSEClient] = None
        self._sse_config = sse_config or SSEConfig()

        # Configure logging
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

        # Auto-start SSE if callback provided
        if self._on_feedback and self.config.is_configured():
            self._start_sse_client()

    @property
    def http_client(self) -> httpx.Client:
        """Get or create HTTP client (lazy initialization)."""
        if self._http_client is None:
            print(f"  [DEBUG] Creating HTTP client for {self.config.base_url}...")
            print(f"  [DEBUG] Acquiring lock for http_client...")
            with self._http_lock:
                print(f"  [DEBUG] Lock acquired, checking if client exists...")
                if self._http_client is None:
                    print(f"  [DEBUG] Building httpx.Client...")
                    self._http_client = httpx.Client(
                        base_url=self.config.base_url,
                        headers={
                            "X-API-Key": self.config.api_key,
                            "Content-Type": "application/json",
                            "User-Agent": "acgp/0.1.0",
                        },
                        timeout=httpx.Timeout(
                            timeout=30.0,  # Default timeout
                            connect=self.config.connect_timeout,
                            read=self.config.read_timeout,
                        ),
                    )
                    print("  [DEBUG] HTTP client created")
        return self._http_client

    @property
    def event_queue(self) -> AsyncEventQueue:
        """Get or create event queue (lazy initialization)."""
        if self._event_queue is None:
            print("  [DEBUG] Creating event queue...")
            with self._queue_lock:
                if self._event_queue is None:
                    # Build queue configuration from client config
                    queue_config = QueueConfig(
                        max_queue_size=self.config.max_queue_size,
                        flush_interval=self.config.flush_interval,
                        batch_size=self.config.batch_size,
                        shutdown_timeout=10.0,
                    )

                    batch_config = BatchConfig(
                        batch_size=self.config.batch_size,
                        compress=True,
                        compression_threshold=1024,
                    )

                    retry_config = RetryConfig(
                        max_retries=self.config.max_retries,
                        base_delay=self.config.retry_base_delay,
                        max_delay=self.config.retry_max_delay,
                        circuit_breaker_enabled=True,
                    )

                    print("  [DEBUG] About to get http_client for queue...")
                    http_client = self.http_client
                    print("  [DEBUG] Got http_client, creating AsyncEventQueue...")
                    self._event_queue = AsyncEventQueue(
                        http_client=http_client,
                        config=queue_config,
                        batch_config=batch_config,
                        retry_config=retry_config,
                        on_flush_complete=self._on_flush_complete,
                    )
                    print("  [DEBUG] Event queue created")

        return self._event_queue

    def _ensure_queue_started(self) -> None:
        """Ensure the background queue is started."""
        if not self._queue_started:
            # Get queue first (may acquire lock internally)
            queue = self.event_queue
            # Then start it with lock protection for the flag
            with self._queue_lock:
                if not self._queue_started:
                    queue.start()
                    self._queue_started = True
                    logger.debug("Event queue started")

    def _start_sse_client(self) -> None:
        """Start the SSE client for real-time feedback streaming."""
        if self._sse_client is not None:
            return  # Already started

        def on_sse_connected():
            logger.info("SSE stream connected - receiving real-time feedback")

        def on_sse_error(error: Exception):
            logger.warning(f"SSE stream error: {error}")

        self._sse_client = SSEClient(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            on_feedback=self._on_feedback,
            on_connected=on_sse_connected,
            on_error=on_sse_error,
            config=self._sse_config,
        )
        self._sse_client.start()
        logger.debug("SSE client started for real-time feedback")

    def _stop_sse_client(self, timeout: float = 5.0) -> None:
        """Stop the SSE client."""
        if self._sse_client is not None:
            self._sse_client.stop(timeout=timeout)
            self._sse_client = None
            logger.debug("SSE client stopped")

    def _register_pending_trace(self, trace_id: str) -> None:
        """Register a trace as pending feedback (for SSE tracking)."""
        if self._sse_client is not None:
            self._sse_client.register_pending_trace(trace_id)

    @property
    def sse_connected(self) -> bool:
        """Check if SSE stream is connected."""
        return self._sse_client is not None and self._sse_client.is_connected

    @property
    def pending_feedback_count(self) -> int:
        """Number of traces waiting for feedback via SSE."""
        if self._sse_client is not None:
            return self._sse_client.pending_count
        return 0

    def wait_for_feedback(self, timeout: Optional[float] = None, auto_flush: bool = True) -> bool:
        """
        Wait for all pending traces to receive feedback via SSE.

        This method automatically flushes pending traces before waiting,
        ensuring traces are sent to the backend before waiting for feedback.

        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)
            auto_flush: If True (default), flush pending traces before waiting

        Returns:
            True if all feedback received, False if timeout or SSE not enabled
        """
        if self._sse_client is None:
            logger.warning("SSE not enabled - cannot wait for feedback")
            return False

        # Auto-flush traces before waiting - can't get feedback on unsent traces
        if auto_flush:
            self.flush()

        return self._sse_client.wait_for_pending(timeout=timeout)

    def trace(
        self,
        agent_type: str,
        goal: str,
        agent_tag: Optional[str] = None,
        user_query: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TraceContext:
        """
        Create a trace context manager for capturing agent execution.

        Args:
            agent_type: Type of agent ("planner", "executor", or custom type)
            goal: The goal the agent is working towards
            agent_tag: Unique identifier for this agent. Recommended to provide
                       a descriptive tag like "inventory-planner" or "crm-executor".
                       If not provided, defaults to "A" for planner, "B" for executor.
                       Using unique tags helps distinguish agents across multiple apps.
            user_query: Original user query (defaults to goal)
            metadata: Additional metadata to include

        Returns:
            TraceContext for use in a with statement

        Example:
            with client.trace(
                agent_type="planner",
                agent_tag="myapp-order-planner",
                goal="Plan order fulfillment"
            ) as trace:
                result = planner.run()
                trace.set_output(result)
        """
        return TraceContext(
            client=self,
            agent_type=agent_type,
            goal=goal,
            agent_tag=agent_tag,
            user_query=user_query,
            metadata=metadata,
        )

    def capture_trace(
        self,
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
    ) -> str:
        """
        Manually capture an agent trace.

        Args:
            agent_type: Type of agent ("planner", "executor", or custom type)
            goal: The goal the agent is working towards
            reasoning_text: The agent's reasoning/thought process
            final_output: The agent's final output/result
            agent_tag: Unique identifier for this agent. Recommended to provide
                       a descriptive tag like "inventory-planner" or "crm-executor".
                       If not provided, defaults to "A" for planner, "B" for executor.
            user_query: Original user query (defaults to goal)
            output_type: Type of output ("plan", "execution_result", etc.)
            context_information: Additional context data
            documents_used: List of document filenames used
            similarity_scores: Similarity scores for retrieved documents

        Returns:
            trace_id: Unique identifier for this trace
        """
        trace_id = str(uuid.uuid4())

        if agent_tag is None:
            agent_tag = "A" if agent_type.lower() == "planner" else "B"

        trace_data = {
            "trace_id": trace_id,
            "agent_type": agent_type,
            "agent_tag": agent_tag,
            "goal": goal,
            "user_query": user_query or goal,
            "reasoning_text": reasoning_text,
            "final_output": final_output,
            "output_type": output_type,
            "context_information": context_information or {},
            "documents_used": documents_used,
            "similarity_scores": similarity_scores,
            "timestamp": datetime.now().isoformat(),
        }

        self._send_trace(trace_data)
        return trace_id

    def _send_trace(self, trace_data: Dict[str, Any]) -> bool:
        """
        Queue a trace for async sending to the backend.

        Non-blocking: trace is added to background queue for batched delivery.

        Args:
            trace_data: Trace event dictionary

        Returns:
            True if trace was queued, False if queue is full or SDK disabled
        """
        print("  [DEBUG] _send_trace() called")
        if not self.config.enabled:
            logger.debug("SDK disabled, skipping trace")
            return False

        if not self.config.is_configured():
            logger.warning("AACGP SDK not configured (missing API key), skipping trace")
            return False

        try:
            # Ensure background queue is running
            print("  [DEBUG] About to ensure queue started...")
            self._ensure_queue_started()
            print("  [DEBUG] Queue started, about to enqueue...")

            # Add trace to async queue (non-blocking)
            queued = self.event_queue.enqueue(trace_data)
            print(f"  [DEBUG] Enqueue result: {queued}")

            if queued:
                trace_id = trace_data.get('trace_id')
                logger.debug(f"Trace queued: {trace_id}")

                # Register for SSE feedback if enabled
                if trace_id and self._sse_client is not None:
                    self._register_pending_trace(trace_id)
            else:
                logger.warning(f"Queue full, trace dropped: {trace_data.get('trace_id')}")

            return queued

        except Exception as e:
            print(f"  [DEBUG] Exception in _send_trace: {e}")
            if self.config.fail_silently:
                logger.warning(f"Failed to queue trace: {e}")
                return False
            raise

    def _send_trace_sync(self, trace_data: Dict[str, Any]) -> None:
        """
        Send a trace synchronously (bypasses queue).

        Use for urgent traces or when async queue is not suitable.
        """
        if not self.config.enabled or not self.config.is_configured():
            return

        try:
            response = self.http_client.post("/ingest/traces", json=trace_data)
            response.raise_for_status()
            logger.debug(f"Trace sent synchronously: {trace_data.get('trace_id')}")
        except httpx.HTTPError as e:
            if self.config.fail_silently:
                logger.warning(f"Failed to send trace: {e}")
            else:
                raise

    def get_score(
        self,
        trace_id: str,
        wait_for_processing: bool = True,
        max_attempts: int = 5,
        initial_delay: float = 1.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the CTQ score for a trace.

        Args:
            trace_id: The trace identifier
            wait_for_processing: If True, retry until trace is processed (default: True)
            max_attempts: Maximum retry attempts when waiting (default: 5)
            initial_delay: Initial delay between retries in seconds (default: 1.0)

        Returns:
            CTQ score data or None if not available
        """
        if not self.config.enabled or not self.config.is_configured():
            return None

        import time
        delay = initial_delay
        last_result = None

        for attempt in range(max_attempts):
            try:
                response = self.http_client.get(f"/query/scores/{trace_id}")
                response.raise_for_status()
                result = response.json()
                last_result = result

                # Check if trace is processed
                if not wait_for_processing:
                    return result

                status = result.get("status", "")
                if status != "not_found" and result.get("scores") is not None:
                    logger.debug(f"Score retrieved for {trace_id} on attempt {attempt + 1}")
                    return result

                # Trace not yet processed, retry
                if attempt < max_attempts - 1:
                    logger.debug(f"Trace {trace_id} not yet processed, retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= 1.5  # Exponential backoff

            except httpx.HTTPError as e:
                if self.config.fail_silently:
                    logger.warning(f"Failed to get score (attempt {attempt + 1}): {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        delay *= 1.5
                    continue
                raise

        logger.debug(f"Score not available for {trace_id} after {max_attempts} attempts")
        return last_result

    def get_feedback(
        self,
        trace_id: str,
        wait_for_processing: bool = True,
        max_attempts: int = 5,
        initial_delay: float = 1.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Get oversight feedback for a trace.

        Args:
            trace_id: The trace identifier
            wait_for_processing: If True, retry until trace is processed (default: True)
            max_attempts: Maximum retry attempts when waiting (default: 5)
            initial_delay: Initial delay between retries in seconds (default: 1.0)

        Returns:
            Feedback data (socratic nudge, HITL alert, etc.) or None
        """
        if not self.config.enabled or not self.config.is_configured():
            return None

        import time
        delay = initial_delay
        last_result = None

        for attempt in range(max_attempts):
            try:
                response = self.http_client.get(f"/query/feedback/{trace_id}")
                response.raise_for_status()
                result = response.json()
                last_result = result

                # Check if trace is processed
                if not wait_for_processing:
                    return result

                status = result.get("status", "")
                if status != "not_found" and result.get("feedback") is not None:
                    logger.debug(f"Feedback retrieved for {trace_id} on attempt {attempt + 1}")
                    return result

                # Trace not yet processed, retry
                if attempt < max_attempts - 1:
                    logger.debug(f"Trace {trace_id} feedback not yet available, retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    delay *= 1.5  # Exponential backoff

            except httpx.HTTPError as e:
                if self.config.fail_silently:
                    logger.warning(f"Failed to get feedback (attempt {attempt + 1}): {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        delay *= 1.5
                    continue
                raise

        logger.debug(f"Feedback not available for {trace_id} after {max_attempts} attempts")
        return last_result

    def get_oversight_mode(self, trace_id: str) -> Optional[str]:
        """
        Get the current oversight mode for a trace.

        Args:
            trace_id: The trace identifier

        Returns:
            Oversight mode ("socratic_philosopher", "wise_critic", "strict_guardian") or None
        """
        if not self.config.enabled or not self.config.is_configured():
            return None

        try:
            response = self.http_client.get(f"/query/oversight/{trace_id}")
            response.raise_for_status()
            data = response.json()
            return data.get("oversight_mode")
        except httpx.HTTPError as e:
            if self.config.fail_silently:
                logger.warning(f"Failed to get oversight mode: {e}")
                return None
            raise

    def flush(self) -> List[BatchResult]:
        """
        Force flush any pending traces immediately.

        This sends all queued traces in batches without waiting for
        the flush interval. Useful before shutdown or when you need
        traces to be sent immediately.

        Returns:
            List of BatchResult objects from the flush operation
        """
        if self._event_queue is None or not self._queue_started:
            return []

        try:
            results = self.event_queue.flush()
            logger.debug(f"Manual flush completed: {len(results)} batches sent")
            return results
        except Exception as e:
            if self.config.fail_silently:
                logger.warning(f"Flush failed: {e}")
                return []
            raise

    def close(self, timeout: Optional[float] = None) -> None:
        """
        Close the client and release resources.

        This will flush any pending traces and stop SSE streaming before closing.
        Should be called when done using the client.

        Args:
            timeout: Max seconds to wait for flush (default: 10s)
        """
        # Stop SSE client first
        self._stop_sse_client(timeout=timeout or 5.0)

        # Stop the event queue (flushes remaining events)
        if self._event_queue is not None:
            try:
                self._event_queue.stop(timeout=timeout)
                logger.debug("Event queue stopped")
            except Exception as e:
                logger.warning(f"Error stopping event queue: {e}")
            self._event_queue = None
            self._queue_started = False

        # Close HTTP client
        if self._http_client is not None:
            self._http_client.close()
            self._http_client = None

        logger.debug("CGP client closed")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get SDK metrics including queue, transport, and SSE statistics.

        Returns:
            Dictionary with queue size, events sent/dropped, SSE status, etc.
        """
        metrics = {
            "enabled": self.config.enabled,
            "configured": self.config.is_configured(),
            "queue_started": self._queue_started,
            "sse_enabled": self._on_feedback is not None,
            "sse_connected": self.sse_connected,
            "pending_feedback": self.pending_feedback_count,
        }

        if self._event_queue is not None:
            metrics.update(self.event_queue.get_metrics())

        return metrics

    def __enter__(self) -> "ACGPClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


def acgp_trace(
    client: ACGPClient,
    agent_type: str,
    agent_tag: Optional[str] = None,
    goal: Optional[str] = None,
    extract_output: bool = True,
):
    """
    Decorator for automatically tracing agent function calls.

    Usage:
        @acgp_trace(client, agent_type="planner", agent_tag="myapp-planner")
        def my_agent_function(query: str) -> str:
            return process(query)

    Args:
        client: ACGPClient instance
        agent_type: Type of agent ("planner", "executor", or custom type)
        agent_tag: Unique identifier for this agent. Recommended to provide
                   a descriptive tag like "inventory-planner" or "crm-executor".
                   If not provided, defaults to "A" for planner, "B" for executor.
        goal: Optional fixed goal (if not provided, uses first arg)
        extract_output: Whether to capture return value as final_output
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine goal
            trace_goal = goal
            if trace_goal is None and args:
                trace_goal = str(args[0])[:500]  # Use first arg, truncated

            with client.trace(
                agent_type=agent_type,
                agent_tag=agent_tag,
                goal=trace_goal or "Agent execution"
            ) as trace:
                result = func(*args, **kwargs)
                if extract_output and result is not None:
                    trace.set_output(str(result))
                return result
        return wrapper
    return decorator
