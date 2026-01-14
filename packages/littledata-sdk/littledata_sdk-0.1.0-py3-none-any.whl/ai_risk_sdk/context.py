"""Context managers for tracking AI interactions."""

import time
import uuid
from contextlib import contextmanager
from typing import Any, Callable

from ai_risk_sdk.client import AIRiskClient


class AIContext:
    """Context for tracking a single AI interaction flow."""

    def __init__(
        self,
        client: AIRiskClient,
        model_id: str | None = None,
        model_provider: str | None = None,
        trace_id: str | uuid.UUID | None = None,
    ):
        self.client = client
        self.model_id = model_id
        self.model_provider = model_provider
        self.trace_id = str(trace_id) if trace_id else str(uuid.uuid4())
        self._start_time = time.perf_counter()
        self._span_count = 0

    def record_prompt(self, prompt: str, **kwargs) -> str:
        """Record a prompt within this context."""
        return self.client.record_prompt(
            prompt=prompt,
            trace_id=self.trace_id,
            model_id=kwargs.get("model_id", self.model_id),
            model_provider=kwargs.get("model_provider", self.model_provider),
            **{k: v for k, v in kwargs.items() if k not in ("model_id", "model_provider")},
        )

    def record_response(self, response: str, **kwargs) -> str:
        """Record a response within this context."""
        latency_ms = kwargs.get("latency_ms")
        if latency_ms is None:
            latency_ms = int((time.perf_counter() - self._start_time) * 1000)

        return self.client.record_response(
            response=response,
            trace_id=self.trace_id,
            model_id=kwargs.get("model_id", self.model_id),
            model_provider=kwargs.get("model_provider", self.model_provider),
            latency_ms=latency_ms,
            **{k: v for k, v in kwargs.items() if k not in ("model_id", "model_provider", "latency_ms")},
        )

    def record_tool_call(
        self,
        tool_name: str,
        input_data: Any = None,
        output_data: Any = None,
        **kwargs,
    ) -> str:
        """Record a tool call within this context."""
        self._span_count += 1
        return self.client.record_event(
            event_type="tool_call",
            trace_id=self.trace_id,
            attributes={
                "tool_name": tool_name,
                "input": str(input_data) if input_data else None,
                "output": str(output_data) if output_data else None,
                "span_number": self._span_count,
                **kwargs.get("attributes", {}),
            },
            **{k: v for k, v in kwargs.items() if k != "attributes"},
        )

    def wrap_tool_call(
        self,
        tool_name: str,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Wrap a tool call and automatically record it.

        Usage:
            result = ctx.wrap_tool_call("web_search", search_function, query="test")
        """
        input_data = {"args": args, "kwargs": kwargs}
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            latency_ms = int((time.perf_counter() - start) * 1000)

            self.record_tool_call(
                tool_name=tool_name,
                input_data=input_data,
                output_data=result,
                attributes={"latency_ms": latency_ms, "success": True},
            )
            return result

        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            self.record_tool_call(
                tool_name=tool_name,
                input_data=input_data,
                output_data=None,
                attributes={
                    "latency_ms": latency_ms,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise

    async def wrap_tool_call_async(
        self,
        tool_name: str,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """Async version of wrap_tool_call."""
        input_data = {"args": args, "kwargs": kwargs}
        start = time.perf_counter()

        try:
            result = await func(*args, **kwargs)
            latency_ms = int((time.perf_counter() - start) * 1000)

            self.record_tool_call(
                tool_name=tool_name,
                input_data=input_data,
                output_data=result,
                attributes={"latency_ms": latency_ms, "success": True},
            )
            return result

        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            self.record_tool_call(
                tool_name=tool_name,
                input_data=input_data,
                output_data=None,
                attributes={
                    "latency_ms": latency_ms,
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )
            raise


@contextmanager
def ai_context(
    client: AIRiskClient,
    model_id: str | None = None,
    model_provider: str | None = None,
    trace_id: str | uuid.UUID | None = None,
):
    """Context manager for tracking AI interactions.

    Usage:
        with ai_context(client, model_id="gpt-4") as ctx:
            ctx.record_prompt("Hello, world!")
            response = call_ai_model(...)
            ctx.record_response(response)

    Args:
        client: AIRiskClient instance
        model_id: The model identifier
        model_provider: The provider
        trace_id: Optional trace ID (generates one if not provided)
    """
    ctx = AIContext(
        client=client,
        model_id=model_id,
        model_provider=model_provider,
        trace_id=trace_id,
    )
    try:
        yield ctx
    except Exception as e:
        # Record error
        client.record_event(
            event_type="error",
            trace_id=ctx.trace_id,
            model_id=model_id,
            model_provider=model_provider,
            attributes={"error": str(e), "error_type": type(e).__name__},
        )
        raise
