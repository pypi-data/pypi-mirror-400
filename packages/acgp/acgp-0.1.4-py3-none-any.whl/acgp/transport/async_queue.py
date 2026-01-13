"""
CGP SDK Async Event Queue

Thread-safe queue with background flusher for non-blocking event sending.
"""

import queue
import threading
import logging
import atexit
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime

import httpx

from .batch_sender import BatchSender, BatchConfig, BatchResult
from .retry import RetryConfig


logger = logging.getLogger("acgp.transport")


@dataclass
class QueueConfig:
    """Configuration for the async queue."""
    max_queue_size: int = 10000  # Max events in memory
    flush_interval: float = 5.0  # Seconds between flushes
    batch_size: int = 100  # Events per batch
    shutdown_timeout: float = 10.0  # Seconds to wait on shutdown


class AsyncEventQueue:
    """
    Thread-safe event queue with background flushing.

    Features:
    - Non-blocking enqueue (never blocks the caller)
    - Background thread for periodic flushing
    - Batched sending for efficiency
    - Graceful shutdown with drain
    - Overflow handling (drops oldest events)

    Usage:
        queue = AsyncEventQueue(http_client, config)
        queue.start()

        # Add events (non-blocking)
        queue.enqueue({"trace_id": "...", ...})

        # Shutdown gracefully
        queue.stop()
    """

    def __init__(
        self,
        http_client: httpx.Client,
        config: Optional[QueueConfig] = None,
        batch_config: Optional[BatchConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        on_flush_complete: Optional[Callable[[List[BatchResult]], None]] = None,
    ):
        """
        Initialize the async queue.

        Args:
            http_client: Configured httpx client
            config: Queue configuration
            batch_config: Batch sender configuration
            retry_config: Retry configuration
            on_flush_complete: Optional callback after each flush
        """
        self.config = config or QueueConfig()
        self.http_client = http_client
        self.on_flush_complete = on_flush_complete

        # Thread-safe queue
        self._queue: queue.Queue = queue.Queue(maxsize=self.config.max_queue_size)

        # Batch sender
        self._batch_sender = BatchSender(
            http_client=http_client,
            batch_config=batch_config or BatchConfig(batch_size=self.config.batch_size),
            retry_config=retry_config,
        )

        # Background thread
        self._flush_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._started = False

        # Metrics
        self._events_enqueued = 0
        self._events_dropped = 0
        self._flushes_completed = 0

        # Register shutdown handler
        atexit.register(self._atexit_handler)

    def start(self) -> None:
        """Start the background flush thread."""
        if self._started:
            return

        self._stop_event.clear()
        self._flush_thread = threading.Thread(
            target=self._flush_loop,
            name="acgp-flush",
            daemon=True,  # Don't prevent program exit
        )
        self._flush_thread.start()
        self._started = True
        logger.debug("Async queue started")

    def stop(self, timeout: Optional[float] = None) -> None:
        """
        Stop the background thread and flush remaining events.

        Args:
            timeout: Max seconds to wait (default: config.shutdown_timeout)
        """
        if not self._started:
            return

        timeout = timeout or self.config.shutdown_timeout

        # Signal thread to stop
        self._stop_event.set()

        # Wait for thread to finish
        if self._flush_thread and self._flush_thread.is_alive():
            self._flush_thread.join(timeout=timeout)

        # Final flush of any remaining events
        self._flush_remaining()

        self._started = False
        logger.debug("Async queue stopped")

    def enqueue(self, event: Dict[str, Any]) -> bool:
        """
        Add an event to the queue (non-blocking).

        Args:
            event: Event dictionary to queue

        Returns:
            True if enqueued, False if queue is full (event dropped)
        """
        try:
            self._queue.put_nowait(event)
            self._events_enqueued += 1
            return True
        except queue.Full:
            # Queue is full - drop the event
            self._events_dropped += 1
            logger.warning(
                f"Queue full ({self.config.max_queue_size}), event dropped. "
                f"Total dropped: {self._events_dropped}"
            )
            return False

    def flush(self) -> List[BatchResult]:
        """
        Manually trigger a flush of queued events.

        Returns:
            List of BatchResults from the flush
        """
        events = self._drain_queue()
        if not events:
            return []

        results = self._batch_sender.send_events(events)
        self._flushes_completed += 1

        if self.on_flush_complete:
            try:
                self.on_flush_complete(results)
            except Exception as e:
                logger.error(f"Flush callback error: {e}")

        return results

    def _flush_loop(self) -> None:
        """Background thread loop for periodic flushing."""
        while not self._stop_event.is_set():
            # Wait for flush interval or stop signal
            self._stop_event.wait(timeout=self.config.flush_interval)

            if self._stop_event.is_set():
                break

            # Flush events
            try:
                self.flush()
            except Exception as e:
                logger.error(f"Error in flush loop: {e}")

    def _drain_queue(self) -> List[Dict[str, Any]]:
        """Drain all events from the queue."""
        events = []
        while True:
            try:
                event = self._queue.get_nowait()
                events.append(event)
            except queue.Empty:
                break
        return events

    def _flush_remaining(self) -> None:
        """Flush any remaining events (called on shutdown)."""
        events = self._drain_queue()
        if events:
            logger.info(f"Flushing {len(events)} remaining events on shutdown")
            try:
                self._batch_sender.send_events(events)
            except Exception as e:
                logger.error(f"Error flushing remaining events: {e}")

    def _atexit_handler(self) -> None:
        """Handler called on program exit."""
        if self._started:
            logger.debug("atexit: stopping async queue")
            self.stop(timeout=5.0)

    @property
    def queue_size(self) -> int:
        """Current number of events in queue."""
        return self._queue.qsize()

    @property
    def is_running(self) -> bool:
        """Check if background thread is running."""
        return self._started and self._flush_thread is not None and self._flush_thread.is_alive()

    def get_metrics(self) -> Dict[str, Any]:
        """Get queue metrics."""
        sender_metrics = self._batch_sender.get_metrics()
        return {
            "queue_size": self.queue_size,
            "events_enqueued": self._events_enqueued,
            "events_dropped": self._events_dropped,
            "flushes_completed": self._flushes_completed,
            "is_running": self.is_running,
            **sender_metrics,
        }
