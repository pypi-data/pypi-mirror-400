"""SDK configuration."""

from dataclasses import dataclass, field


@dataclass
class SDKConfig:
    """Configuration for the AI Risk SDK."""

    # API connection
    api_key: str
    endpoint: str = "https://littledata.ai"

    # Batching
    batch_size: int = 100
    flush_interval_ms: int = 1000

    # Features
    enable_dlp: bool = True
    hash_prompts: bool = True
    async_mode: bool = True

    # Retry settings
    max_retries: int = 3
    retry_delay_ms: int = 100

    # Timeout
    timeout_ms: int = 5000

    # Circuit breaker
    circuit_breaker_threshold: int = 5
    circuit_breaker_reset_ms: int = 30000

    def __post_init__(self):
        if not self.api_key:
            raise ValueError("api_key is required")
        if not self.endpoint:
            raise ValueError("endpoint is required")
