"""
Telemetry Client Protocol

Port for telemetry/observability systems.
"""
from abc import abstractmethod
from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class TelemetryClientProtocol(Protocol):
    """Interface for telemetry and observability"""

    @abstractmethod
    def record_event(
        self,
        event_type: str,
        actor_type: str,
        source: str,
        metadata: Dict[str, Any],
    ) -> None:
        """
        Record a telemetry event.

        Args:
            event_type: Type of event (e.g., "agent_execution")
            actor_type: Actor that generated event (e.g., "agent")
            source: Source system (e.g., "axis-reasoning")
            metadata: Event-specific metadata
        """
        ...

    @abstractmethod
    def record_tokens(
        self,
        agent_id: str,
        tokens_used: int,
        cached_tokens: int = 0,
        cost_estimate: float = 0.0,
    ) -> None:
        """
        Record token usage.

        Args:
            agent_id: Agent that consumed tokens
            tokens_used: Number of tokens used
            cached_tokens: Number of cached tokens (if applicable)
            cost_estimate: Estimated cost in USD
        """
        ...
