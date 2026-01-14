"""Client-side DLP integration."""

from dataclasses import dataclass
from typing import Any

from ai_risk_sdk.client import AIRiskClient


@dataclass
class DLPFinding:
    """A DLP finding."""

    type: str
    confidence: float
    location: dict[str, int] | None = None
    message: str | None = None


@dataclass
class DLPResult:
    """Result of a DLP evaluation."""

    action: str  # "allow", "block", "redact"
    content: str  # Original or redacted content
    findings: list[DLPFinding]

    @property
    def is_blocked(self) -> bool:
        return self.action == "block"

    @property
    def is_redacted(self) -> bool:
        return self.action == "redact"

    @property
    def has_findings(self) -> bool:
        return len(self.findings) > 0


class DLPProcessor:
    """Process content through DLP policies.

    Usage:
        client = AIRiskClient(api_key="...")
        dlp = DLPProcessor(client)

        # Check input before sending to AI
        result = await dlp.process_input(user_prompt)
        if result.is_blocked:
            raise BlockedContentError(result.findings)

        # Use result.content (may be redacted)
        response = await call_ai(result.content)

        # Check output before returning to user
        result = await dlp.process_output(response)
        return result.content
    """

    def __init__(self, client: AIRiskClient):
        self.client = client

    async def process_input(
        self,
        content: str,
        model_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> DLPResult:
        """Process input content through DLP.

        Args:
            content: The content to check
            model_id: Optional model identifier
            context: Optional context for policy evaluation

        Returns:
            DLPResult with action and potentially redacted content
        """
        result = await self.client.evaluate_dlp(
            content=content,
            direction="input",
            model_id=model_id,
            context=context,
        )
        return self._parse_result(content, result)

    async def process_output(
        self,
        content: str,
        model_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> DLPResult:
        """Process output content through DLP.

        Args:
            content: The content to check
            model_id: Optional model identifier
            context: Optional context for policy evaluation

        Returns:
            DLPResult with action and potentially redacted content
        """
        result = await self.client.evaluate_dlp(
            content=content,
            direction="output",
            model_id=model_id,
            context=context,
        )
        return self._parse_result(content, result)

    def process_input_sync(
        self,
        content: str,
        model_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> DLPResult:
        """Synchronous version of process_input."""
        result = self.client.evaluate_dlp_sync(
            content=content,
            direction="input",
            model_id=model_id,
            context=context,
        )
        return self._parse_result(content, result)

    def process_output_sync(
        self,
        content: str,
        model_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> DLPResult:
        """Synchronous version of process_output."""
        result = self.client.evaluate_dlp_sync(
            content=content,
            direction="output",
            model_id=model_id,
            context=context,
        )
        return self._parse_result(content, result)

    def _parse_result(self, original_content: str, result: dict) -> DLPResult:
        """Parse the DLP API result into a DLPResult object."""
        action = result.get("action", "allow")
        redacted_content = result.get("redacted_content")
        findings_data = result.get("findings", [])

        findings = [
            DLPFinding(
                type=f.get("type", "unknown"),
                confidence=f.get("confidence", 0.0),
                location=f.get("location"),
                message=f.get("message"),
            )
            for f in findings_data
        ]

        # Use redacted content if available, otherwise original
        content = redacted_content if redacted_content else original_content

        return DLPResult(
            action=action,
            content=content,
            findings=findings,
        )


class BlockedContentError(Exception):
    """Raised when content is blocked by DLP policy."""

    def __init__(self, findings: list[DLPFinding]):
        self.findings = findings
        message = f"Content blocked by DLP policy: {len(findings)} finding(s)"
        super().__init__(message)
