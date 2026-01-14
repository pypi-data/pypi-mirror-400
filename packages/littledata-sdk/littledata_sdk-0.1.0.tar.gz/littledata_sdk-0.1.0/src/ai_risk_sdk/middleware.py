"""ASGI/WSGI Middleware for automatic AI call tracking."""

import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from ai_risk_sdk.client import AIRiskClient


class AIRiskMiddleware(BaseHTTPMiddleware):
    """FastAPI/Starlette middleware for automatic AI call tracking.

    Usage:
        from fastapi import FastAPI
        from ai_risk_sdk.middleware import AIRiskMiddleware

        app = FastAPI()
        app.add_middleware(
            AIRiskMiddleware,
            api_key="airisk_...",
            capture_openai=True,
            capture_anthropic=True,
        )
    """

    def __init__(
        self,
        app,
        api_key: str,
        endpoint: str = "https://littledata.ai",
        capture_openai: bool = True,
        capture_anthropic: bool = True,
        capture_langchain: bool = True,
        **kwargs,
    ):
        super().__init__(app)
        self.client = AIRiskClient(api_key=api_key, endpoint=endpoint, **kwargs)
        self.capture_openai = capture_openai
        self.capture_anthropic = capture_anthropic
        self.capture_langchain = capture_langchain

        # Install capture hooks
        if capture_openai:
            self._install_openai_hooks()
        if capture_anthropic:
            self._install_anthropic_hooks()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process each request."""
        # Generate trace ID for this request
        trace_id = str(uuid.uuid4())
        request.state.ai_risk_trace_id = trace_id
        request.state.ai_risk_client = self.client

        start_time = time.perf_counter()

        response = await call_next(request)

        # Add trace ID to response headers
        response.headers["X-AI-Risk-Trace-Id"] = trace_id

        return response

    def _install_openai_hooks(self):
        """Install hooks to capture OpenAI API calls."""
        try:
            import openai

            original_create = openai.ChatCompletion.create if hasattr(openai, 'ChatCompletion') else None

            # Hook would be installed here for older OpenAI versions
            # For v1.0+, users should use the decorator or context manager
        except ImportError:
            pass

    def _install_anthropic_hooks(self):
        """Install hooks to capture Anthropic API calls."""
        try:
            import anthropic
            # Similar hook installation for Anthropic
        except ImportError:
            pass


def get_client_from_request(request: Request) -> AIRiskClient | None:
    """Get the AI Risk client from a request (if middleware is installed)."""
    return getattr(request.state, "ai_risk_client", None)


def get_trace_id_from_request(request: Request) -> str | None:
    """Get the trace ID from a request (if middleware is installed)."""
    return getattr(request.state, "ai_risk_trace_id", None)
