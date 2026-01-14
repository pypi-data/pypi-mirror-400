"""Main SDK client."""

import asyncio
import hashlib
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from threading import Lock, Thread
from typing import Any

import httpx

from ai_risk_sdk.config import SDKConfig


class AIRiskClient:
    """Client for the AI Risk Platform.

    Provides low-latency telemetry capture with async batching.
    Target: <5ms added latency at p95.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://littledata.ai",
        batch_size: int = 100,
        flush_interval_ms: int = 1000,
        enable_dlp: bool = True,
        hash_prompts: bool = True,
        **kwargs,
    ):
        self.config = SDKConfig(
            api_key=api_key,
            endpoint=endpoint.rstrip("/"),
            batch_size=batch_size,
            flush_interval_ms=flush_interval_ms,
            enable_dlp=enable_dlp,
            hash_prompts=hash_prompts,
            **kwargs,
        )

        # Event queue for batching
        self._event_queue: deque = deque(maxlen=10000)
        self._queue_lock = Lock()

        # HTTP clients - sync for background flush, async for DLP
        self._sync_client = httpx.Client(
            base_url=self.config.endpoint,
            headers={
                "X-API-Key": self.config.api_key,
                "Content-Type": "application/json",
            },
            timeout=self.config.timeout_ms / 1000,
        )
        self._async_client: httpx.AsyncClient | None = None

        # Background flush thread
        self._running = True
        self._flush_thread = Thread(target=self._background_flush, daemon=True)
        self._flush_thread.start()

        # Circuit breaker state
        self._failure_count = 0
        self._circuit_open = False
        self._circuit_reset_time = 0

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create the async client (lazy initialization)."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.config.endpoint,
                headers={
                    "X-API-Key": self.config.api_key,
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout_ms / 1000,
            )
        return self._async_client

    def close(self):
        """Close the client and flush remaining events."""
        self._running = False
        self._flush_sync()
        self._sync_client.close()
        if self._async_client is not None:
            try:
                asyncio.run(self._async_client.aclose())
            except RuntimeError:
                pass  # Event loop already closed, ignore

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # -------------------------------------------------------------------------
    # Event Recording (Non-blocking)
    # -------------------------------------------------------------------------

    def record_event(
        self,
        event_type: str,
        trace_id: str | uuid.UUID | None = None,
        prompt: str | None = None,
        response: str | None = None,
        model_id: str | None = None,
        model_provider: str | None = None,
        token_count_input: int | None = None,
        token_count_output: int | None = None,
        latency_ms: int | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> str:
        """Record an AI interaction event.

        This method is non-blocking and returns immediately.
        Events are batched and sent asynchronously.

        Returns:
            The trace_id for this event.
        """
        if trace_id is None:
            trace_id = uuid.uuid4()

        event = {
            "event_type": event_type,
            "trace_id": str(trace_id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_id": model_id,
            "model_provider": model_provider,
            "token_count_input": token_count_input,
            "token_count_output": token_count_output,
            "latency_ms": latency_ms,
            "attributes": attributes or {},
        }

        # Hash prompts if enabled
        if prompt:
            if self.config.hash_prompts:
                event["prompt_hash"] = self._hash_content(prompt)
            else:
                event["prompt"] = prompt

        if response:
            if self.config.hash_prompts:
                event["response_hash"] = self._hash_content(response)
            else:
                event["response"] = response

        # Add to queue (non-blocking)
        with self._queue_lock:
            self._event_queue.append(event)

        return str(trace_id)

    def record_prompt(
        self,
        prompt: str,
        trace_id: str | uuid.UUID | None = None,
        model_id: str | None = None,
        model_provider: str | None = None,
        **kwargs,
    ) -> str:
        """Record a prompt event."""
        return self.record_event(
            event_type="prompt",
            trace_id=trace_id,
            prompt=prompt,
            model_id=model_id,
            model_provider=model_provider,
            **kwargs,
        )

    def record_response(
        self,
        response: str,
        trace_id: str | uuid.UUID,
        model_id: str | None = None,
        model_provider: str | None = None,
        token_count_output: int | None = None,
        latency_ms: int | None = None,
        **kwargs,
    ) -> str:
        """Record a response event."""
        return self.record_event(
            event_type="response",
            trace_id=trace_id,
            response=response,
            model_id=model_id,
            model_provider=model_provider,
            token_count_output=token_count_output,
            latency_ms=latency_ms,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # DLP Evaluation (Sync, for blocking scenarios)
    # -------------------------------------------------------------------------

    async def evaluate_dlp(
        self,
        content: str,
        direction: str = "input",
        model_id: str | None = None,
        context: dict | None = None,
    ) -> dict:
        """Evaluate content against DLP policies.

        This is a synchronous call that blocks until the evaluation completes.
        Use for pre-flight checks when you need to block/redact content.

        Returns:
            {
                "action": "allow" | "block" | "redact",
                "redacted_content": str | None,
                "findings": list
            }
        """
        if not self.config.enable_dlp:
            return {"action": "allow", "redacted_content": None, "findings": []}

        try:
            client = self._get_async_client()
            response = await client.post(
                "/api/v1/dlp/evaluate",
                json={
                    "content": content,
                    "direction": direction,
                    "model_id": model_id,
                    "context": context or {},
                },
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            # Fail open - allow content if DLP is unavailable
            return {"action": "allow", "redacted_content": None, "findings": []}

    def evaluate_dlp_sync(
        self,
        content: str,
        direction: str = "input",
        model_id: str | None = None,
        context: dict | None = None,
    ) -> dict:
        """Synchronous wrapper for evaluate_dlp."""
        return asyncio.run(self.evaluate_dlp(content, direction, model_id, context))

    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------

    def _hash_content(self, content: str) -> str:
        """Hash content using SHA-256."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _background_flush(self):
        """Background thread for periodic flushing."""
        while self._running:
            time.sleep(self.config.flush_interval_ms / 1000)
            self._flush_sync()

    def _flush_sync(self):
        """Flush events synchronously using the sync HTTP client."""
        if self._circuit_open:
            if time.time() < self._circuit_reset_time:
                return  # Circuit is open, skip flush
            self._circuit_open = False

        # Get batch of events
        events = []
        with self._queue_lock:
            while self._event_queue and len(events) < self.config.batch_size:
                events.append(self._event_queue.popleft())

        if not events:
            return

        try:
            response = self._sync_client.post(
                "/api/v1/ingest/events",
                json={"events": events},
            )
            response.raise_for_status()
            self._failure_count = 0
        except Exception:
            # Put events back in queue for retry
            with self._queue_lock:
                for event in reversed(events):
                    self._event_queue.appendleft(event)

            self._failure_count += 1
            if self._failure_count >= self.config.circuit_breaker_threshold:
                self._circuit_open = True
                self._circuit_reset_time = time.time() + (
                    self.config.circuit_breaker_reset_ms / 1000
                )

    async def _flush_async(self):
        """Flush queued events asynchronously."""
        if self._circuit_open:
            if time.time() < self._circuit_reset_time:
                return  # Circuit is open, skip flush
            self._circuit_open = False

        # Get batch of events
        events = []
        with self._queue_lock:
            while self._event_queue and len(events) < self.config.batch_size:
                events.append(self._event_queue.popleft())

        if not events:
            return

        try:
            client = self._get_async_client()
            response = await client.post(
                "/api/v1/ingest/events",
                json={"events": events},
            )
            response.raise_for_status()
            self._failure_count = 0
        except Exception:
            # Put events back in queue for retry
            with self._queue_lock:
                for event in reversed(events):
                    self._event_queue.appendleft(event)

            self._failure_count += 1
            if self._failure_count >= self.config.circuit_breaker_threshold:
                self._circuit_open = True
                self._circuit_reset_time = time.time() + (
                    self.config.circuit_breaker_reset_ms / 1000
                )

    async def flush(self):
        """Manually flush queued events (async version)."""
        await self._flush_async()

    def flush_sync(self):
        """Manually flush queued events (sync version)."""
        self._flush_sync()


# Global client instance (optional convenience)
_global_client: AIRiskClient | None = None


def init(api_key: str, **kwargs) -> AIRiskClient:
    """Initialize the global client."""
    global _global_client
    _global_client = AIRiskClient(api_key=api_key, **kwargs)
    return _global_client


def get_client() -> AIRiskClient:
    """Get the global client instance."""
    if _global_client is None:
        raise RuntimeError("SDK not initialized. Call init() first.")
    return _global_client
