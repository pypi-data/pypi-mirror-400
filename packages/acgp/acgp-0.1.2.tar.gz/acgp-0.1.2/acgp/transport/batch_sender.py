"""
CGP SDK Batch Sender

Handles batched HTTP transport with compression and idempotency.
"""

import gzip
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

import httpx

from .retry import RetryHandler, RetryConfig


logger = logging.getLogger("acgp.transport")


@dataclass
class BatchConfig:
    """Configuration for batch sending."""
    batch_size: int = 100  # Max events per batch
    compress: bool = True  # Enable gzip compression
    compression_threshold: int = 1024  # Bytes before compression kicks in


@dataclass
class BatchResult:
    """Result of a batch send operation."""
    success: bool
    batch_id: str
    events_sent: int
    events_failed: int
    error: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None


class BatchSender:
    """
    Sends events in batches with compression and retry support.

    Features:
    - Batches multiple events into single HTTP request
    - Gzip compression for large payloads
    - Idempotency keys to prevent duplicate processing
    - Retry with exponential backoff
    """

    def __init__(
        self,
        http_client: httpx.Client,
        endpoint: str = "/ingest/traces/batch",
        batch_config: Optional[BatchConfig] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize the batch sender.

        Args:
            http_client: Configured httpx client
            endpoint: API endpoint for batch ingestion
            batch_config: Batch configuration
            retry_config: Retry configuration
        """
        self.http_client = http_client
        self.endpoint = endpoint
        self.batch_config = batch_config or BatchConfig()
        self.retry_handler = RetryHandler(retry_config or RetryConfig())

        # Metrics
        self.total_batches_sent = 0
        self.total_events_sent = 0
        self.total_failures = 0

    def send_batch(self, events: List[Dict[str, Any]]) -> BatchResult:
        """
        Send a batch of events to the backend.

        Args:
            events: List of event dictionaries to send

        Returns:
            BatchResult with success/failure information
        """
        if not events:
            return BatchResult(
                success=True,
                batch_id="",
                events_sent=0,
                events_failed=0,
            )

        batch_id = str(uuid.uuid4())

        # Add idempotency keys to events that don't have them
        for event in events:
            if "idempotency_key" not in event:
                event["idempotency_key"] = f"{batch_id}_{event.get('trace_id', uuid.uuid4())}"

        # Build batch payload
        payload = {
            "batch_id": batch_id,
            "events": events,
            "event_count": len(events),
            "timestamp": datetime.now().isoformat(),
        }

        try:
            result = self.retry_handler.execute(
                self._send_payload,
                payload,
                batch_id,
            )
            return result

        except Exception as e:
            logger.error(f"Batch {batch_id} failed after retries: {e}")
            self.total_failures += len(events)
            return BatchResult(
                success=False,
                batch_id=batch_id,
                events_sent=0,
                events_failed=len(events),
                error=str(e),
            )

    def _send_payload(self, payload: Dict[str, Any], batch_id: str) -> BatchResult:
        """
        Send payload to the backend (called by retry handler).

        Args:
            payload: The batch payload
            batch_id: Batch identifier

        Returns:
            BatchResult
        """
        # Serialize payload
        json_data = json.dumps(payload)
        content = json_data.encode("utf-8")

        # Compress if beneficial
        headers = {"Content-Type": "application/json"}
        if self.batch_config.compress and len(content) > self.batch_config.compression_threshold:
            content = gzip.compress(content)
            headers["Content-Encoding"] = "gzip"
            logger.debug(
                f"Batch {batch_id}: Compressed {len(json_data)} -> {len(content)} bytes"
            )

        # Add idempotency header
        headers["X-Idempotency-Key"] = batch_id

        # Send request
        response = self.http_client.post(
            self.endpoint,
            content=content,
            headers=headers,
        )
        response.raise_for_status()

        # Parse response
        response_data = response.json() if response.content else {}
        events_sent = len(payload["events"])

        # Update metrics
        self.total_batches_sent += 1
        self.total_events_sent += events_sent

        logger.debug(f"Batch {batch_id}: Sent {events_sent} events successfully")

        return BatchResult(
            success=True,
            batch_id=batch_id,
            events_sent=events_sent,
            events_failed=0,
            response_data=response_data,
        )

    def send_events(self, events: List[Dict[str, Any]]) -> List[BatchResult]:
        """
        Send events, splitting into batches if necessary.

        Args:
            events: List of events to send

        Returns:
            List of BatchResults (one per batch)
        """
        results = []

        # Split into batches
        for i in range(0, len(events), self.batch_config.batch_size):
            batch = events[i:i + self.batch_config.batch_size]
            result = self.send_batch(batch)
            results.append(result)

        return results

    def get_metrics(self) -> Dict[str, Any]:
        """Get sender metrics."""
        return {
            "total_batches_sent": self.total_batches_sent,
            "total_events_sent": self.total_events_sent,
            "total_failures": self.total_failures,
        }
