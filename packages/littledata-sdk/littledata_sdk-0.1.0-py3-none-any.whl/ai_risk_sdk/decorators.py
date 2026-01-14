"""Decorators for tracking AI calls."""

import functools
import time
import uuid
from typing import Any, Callable

from ai_risk_sdk.client import AIRiskClient


def track_ai_call(
    client: AIRiskClient,
    model_id: str | None = None,
    model_provider: str | None = None,
    capture_prompt: bool = True,
    capture_response: bool = True,
):
    """Decorator to automatically track AI function calls.

    Usage:
        @track_ai_call(client, model_id="gpt-4", provider="openai")
        def generate_response(prompt: str) -> str:
            return openai.chat.completions.create(...)

        @track_ai_call(client, model_id="gpt-4", provider="openai")
        async def generate_response_async(prompt: str) -> str:
            return await openai.chat.completions.acreate(...)

    Args:
        client: AIRiskClient instance
        model_id: The model identifier
        model_provider: The provider (openai, anthropic, etc.)
        capture_prompt: Whether to capture the prompt (first arg)
        capture_response: Whether to capture the response
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            trace_id = uuid.uuid4()
            start_time = time.perf_counter()

            # Extract prompt from first argument
            prompt = None
            if capture_prompt and args:
                prompt = str(args[0]) if args[0] is not None else None

            # Record prompt event
            if prompt:
                client.record_prompt(
                    prompt=prompt,
                    trace_id=trace_id,
                    model_id=model_id,
                    model_provider=model_provider,
                )

            try:
                # Call the wrapped function
                result = await func(*args, **kwargs)

                # Calculate latency
                latency_ms = int((time.perf_counter() - start_time) * 1000)

                # Record response event
                if capture_response and result is not None:
                    response_str = str(result)
                    client.record_response(
                        response=response_str,
                        trace_id=trace_id,
                        model_id=model_id,
                        model_provider=model_provider,
                        latency_ms=latency_ms,
                    )

                return result

            except Exception as e:
                # Record error event
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                client.record_event(
                    event_type="error",
                    trace_id=trace_id,
                    model_id=model_id,
                    model_provider=model_provider,
                    latency_ms=latency_ms,
                    attributes={"error": str(e), "error_type": type(e).__name__},
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            trace_id = uuid.uuid4()
            start_time = time.perf_counter()

            # Extract prompt from first argument
            prompt = None
            if capture_prompt and args:
                prompt = str(args[0]) if args[0] is not None else None

            # Record prompt event
            if prompt:
                client.record_prompt(
                    prompt=prompt,
                    trace_id=trace_id,
                    model_id=model_id,
                    model_provider=model_provider,
                )

            try:
                # Call the wrapped function
                result = func(*args, **kwargs)

                # Calculate latency
                latency_ms = int((time.perf_counter() - start_time) * 1000)

                # Record response event
                if capture_response and result is not None:
                    response_str = str(result)
                    client.record_response(
                        response=response_str,
                        trace_id=trace_id,
                        model_id=model_id,
                        model_provider=model_provider,
                        latency_ms=latency_ms,
                    )

                return result

            except Exception as e:
                # Record error event
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                client.record_event(
                    event_type="error",
                    trace_id=trace_id,
                    model_id=model_id,
                    model_provider=model_provider,
                    latency_ms=latency_ms,
                    attributes={"error": str(e), "error_type": type(e).__name__},
                )
                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Need asyncio for checking coroutine functions
import asyncio
