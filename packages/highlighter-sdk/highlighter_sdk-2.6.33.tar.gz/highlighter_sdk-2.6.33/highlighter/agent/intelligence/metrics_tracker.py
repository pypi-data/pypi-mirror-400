"""Metrics tracking for LLM capability."""

import time
from dataclasses import dataclass, field
from typing import Dict, List

from .config import MonitoringConfig

__all__ = ["MetricsTracker", "StreamMetrics"]


@dataclass
class StreamMetrics:
    """Metrics for a single stream"""

    request_times: List[float] = field(default_factory=list)
    total_cost: float = 0.0
    total_tokens: int = 0
    requests: List[dict] = field(default_factory=list)


class MetricsTracker:
    """Tracks costs, tokens, enforces rate limits

    Monitors LLM API usage, calculates costs using LiteLLM,
    and enforces rate and cost limits.
    """

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.stream_metrics: Dict[str, StreamMetrics] = {}

    def check_rate_limit(self, stream_id: str) -> bool:
        """Check if request is within rate limit

        Args:
            stream_id: Stream identifier

        Returns:
            True if within rate limit, False otherwise
        """
        if self.config.max_requests_per_minute <= 0:
            return True

        metrics = self._get_metrics(stream_id)

        # Remove old requests (>1 minute ago)
        now = time.time()
        cutoff = now - 60.0
        metrics.request_times = [t for t in metrics.request_times if t > cutoff]

        return len(metrics.request_times) < self.config.max_requests_per_minute

    def check_cost_limit(self, stream_id: str) -> bool:
        """Check if stream is within cost limit

        Args:
            stream_id: Stream identifier

        Returns:
            True if within cost limit, False otherwise
        """
        if self.config.max_cost_per_stream is None:
            return True

        metrics = self._get_metrics(stream_id)
        return metrics.total_cost < self.config.max_cost_per_stream

    def record_usage(self, stream_id: str, usage: dict, model: str) -> dict:
        """Record usage and compute costs

        Uses LiteLLM's completion_cost() for accurate pricing.

        Args:
            stream_id: Stream identifier
            usage: Usage dict from LLM response
            model: Model name

        Returns:
            Dict with metrics (tokens, cost, etc.)
        """
        import litellm

        metrics_data = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
            "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
        }

        # Calculate cost using LiteLLM
        try:
            cost = litellm.completion_cost(completion_response={"usage": usage}, model=model)
            metrics_data["estimated_cost"] = cost or 0.0
        except Exception:
            metrics_data["estimated_cost"] = 0.0

        # Update stream metrics
        if self.config.track_metrics:
            metrics = self._get_metrics(stream_id)
            metrics.request_times.append(time.time())
            metrics.total_cost += metrics_data["estimated_cost"]
            metrics.total_tokens += metrics_data["total_tokens"]
            metrics.requests.append(metrics_data)

        return metrics_data

    def get_stream_summary(self, stream_id: str) -> dict:
        """Get summary metrics for a stream

        Args:
            stream_id: Stream identifier

        Returns:
            Dict with summary metrics
        """
        metrics = self._get_metrics(stream_id)
        return {
            "total_requests": len(metrics.requests),
            "total_cost": metrics.total_cost,
            "total_tokens": metrics.total_tokens,
            "avg_tokens_per_request": (
                metrics.total_tokens / len(metrics.requests) if metrics.requests else 0
            ),
        }

    def _get_metrics(self, stream_id: str) -> StreamMetrics:
        """Get or create metrics for stream

        Args:
            stream_id: Stream identifier

        Returns:
            StreamMetrics instance
        """
        if stream_id not in self.stream_metrics:
            self.stream_metrics[stream_id] = StreamMetrics()
        return self.stream_metrics[stream_id]
