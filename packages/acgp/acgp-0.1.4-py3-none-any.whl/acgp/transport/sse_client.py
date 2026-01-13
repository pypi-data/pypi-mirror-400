"""
CGP SDK SSE Client

Real-time Server-Sent Events client for receiving feedback asynchronously.
"""

import json
import logging
import threading
from typing import Optional, Callable, Dict, Any, Set
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger("acgp.sse")


@dataclass
class SSEConfig:
    """Configuration for SSE client."""
    reconnect_delay: float = 1.0  # Initial reconnect delay in seconds
    max_reconnect_delay: float = 30.0  # Maximum reconnect delay
    connection_timeout: float = 10.0  # Connection timeout
    read_timeout: float = 300.0  # Read timeout (5 minutes for long-polling)


class SSEClient:
    """
    Server-Sent Events client for real-time feedback streaming.

    Connects to the Steward backend SSE endpoint and dispatches
    feedback events to registered callbacks.

    Usage:
        def on_feedback(trace_id, data):
            print(f"Feedback for {trace_id}: {data}")

        sse = SSEClient(base_url, api_key, on_feedback=on_feedback)
        sse.start()

        # ... do work ...

        sse.stop()
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        on_feedback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_connected: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        config: Optional[SSEConfig] = None,
    ):
        """
        Initialize SSE client.

        Args:
            base_url: Backend API base URL
            api_key: API key for authentication
            on_feedback: Callback when feedback is received (trace_id, feedback_data)
            on_connected: Callback when connection is established
            on_error: Callback when an error occurs
            config: SSE configuration
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.config = config or SSEConfig()

        # Callbacks
        self._on_feedback = on_feedback
        self._on_connected = on_connected
        self._on_error = on_error

        # State
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._connected = False
        self._pending_traces: Set[str] = set()
        self._pending_lock = threading.Lock()

        # For wait_for_pending
        self._all_processed_event = threading.Event()

    def start(self) -> None:
        """Start the SSE client in a background thread."""
        if self._thread is not None and self._thread.is_alive():
            logger.debug("SSE client already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="acgp-sse",
            daemon=True,
        )
        self._thread.start()
        logger.info("SSE client started")

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the SSE client."""
        self._stop_event.set()

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=timeout)

        self._connected = False
        logger.info("SSE client stopped")

    def register_pending_trace(self, trace_id: str) -> None:
        """Register a trace as pending (waiting for feedback)."""
        with self._pending_lock:
            self._pending_traces.add(trace_id)
            self._all_processed_event.clear()

    def wait_for_pending(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all pending traces to receive feedback.

        Args:
            timeout: Maximum time to wait (None = wait forever)

        Returns:
            True if all traces processed, False if timeout
        """
        with self._pending_lock:
            if not self._pending_traces:
                return True

        return self._all_processed_event.wait(timeout=timeout)

    @property
    def is_connected(self) -> bool:
        """Check if SSE connection is active."""
        return self._connected

    @property
    def pending_count(self) -> int:
        """Number of traces waiting for feedback."""
        with self._pending_lock:
            return len(self._pending_traces)

    def _run_loop(self) -> None:
        """Main SSE connection loop with reconnection."""
        reconnect_delay = self.config.reconnect_delay

        while not self._stop_event.is_set():
            try:
                self._connect_and_listen()
            except Exception as e:
                self._connected = False

                if self._stop_event.is_set():
                    break

                logger.warning(f"SSE connection error: {e}. Reconnecting in {reconnect_delay:.1f}s...")

                if self._on_error:
                    try:
                        self._on_error(e)
                    except Exception as callback_error:
                        logger.error(f"Error in on_error callback: {callback_error}")

                # Wait before reconnecting
                self._stop_event.wait(timeout=reconnect_delay)

                # Exponential backoff
                reconnect_delay = min(
                    reconnect_delay * 1.5,
                    self.config.max_reconnect_delay
                )

        self._connected = False

    def _connect_and_listen(self) -> None:
        """Connect to SSE endpoint and process events."""
        # SSE endpoint - SDK uses httpx which supports custom headers (unlike browser EventSource)
        # Note: base_url already includes /v1 from config, so just add /stream/traces
        url = f"{self.base_url}/stream/traces"

        logger.debug(f"Connecting to SSE: {url}")

        with httpx.Client(timeout=httpx.Timeout(
            connect=self.config.connection_timeout,
            read=self.config.read_timeout,
            write=10.0,
            pool=10.0,
        )) as client:
            with client.stream(
                "GET",
                url,
                headers={
                    "Accept": "text/event-stream",
                    "X-API-Key": self.api_key,
                },
            ) as response:
                response.raise_for_status()
                self._connected = True
                logger.info("SSE connected")

                # Process SSE stream
                event_type = None
                event_data = []

                for line in response.iter_lines():
                    if self._stop_event.is_set():
                        break

                    if not line:
                        # Empty line = end of event
                        if event_type and event_data:
                            self._process_event(event_type, "\n".join(event_data))
                        event_type = None
                        event_data = []
                        continue

                    if line.startswith("event:"):
                        event_type = line[6:].strip()
                    elif line.startswith("data:"):
                        event_data.append(line[5:].strip())
                    elif line.startswith(":"):
                        # Comment/heartbeat, ignore
                        pass

    def _process_event(self, event_type: str, data: str) -> None:
        """Process a received SSE event."""
        logger.debug(f"SSE event: {event_type}")

        try:
            parsed_data = json.loads(data) if data else {}
        except json.JSONDecodeError:
            parsed_data = {"raw": data}

        if event_type == "connected":
            logger.info(f"SSE stream connected: {parsed_data}")
            if self._on_connected:
                try:
                    self._on_connected()
                except Exception as e:
                    logger.error(f"Error in on_connected callback: {e}")

        elif event_type == "trace_processed":
            self._handle_trace_processed(parsed_data)

        elif event_type == "feedback_generated":
            self._handle_feedback_generated(parsed_data)

        elif event_type == "heartbeat":
            logger.debug("SSE heartbeat received")

    def _handle_trace_processed(self, data: Dict[str, Any]) -> None:
        """Handle trace_processed event."""
        trace_id = data.get("trace_id")
        if not trace_id:
            return

        logger.debug(f"Trace processed: {trace_id}")

        # If we have feedback data, dispatch it
        if self._on_feedback and ("feedback" in data or "ctq_scores" in data):
            try:
                self._on_feedback(trace_id, data)
            except Exception as e:
                logger.error(f"Error in on_feedback callback: {e}")

        # Remove from pending
        self._mark_trace_complete(trace_id)

    def _handle_feedback_generated(self, data: Dict[str, Any]) -> None:
        """Handle feedback_generated event."""
        trace_id = data.get("trace_id")
        if not trace_id:
            return

        logger.debug(f"Feedback generated: {trace_id}")

        if self._on_feedback:
            try:
                self._on_feedback(trace_id, data)
            except Exception as e:
                logger.error(f"Error in on_feedback callback: {e}")

        # Remove from pending
        self._mark_trace_complete(trace_id)

    def _mark_trace_complete(self, trace_id: str) -> None:
        """Mark a trace as complete (feedback received)."""
        with self._pending_lock:
            self._pending_traces.discard(trace_id)

            if not self._pending_traces:
                self._all_processed_event.set()
