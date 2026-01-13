"""
Session Ledger Protocol

Port for session state and cognitive history tracking.
"""
from abc import abstractmethod
from typing import Any, Dict, Optional, Protocol, runtime_checkable


@runtime_checkable
class LedgerProtocol(Protocol):
    """Interface for session ledger / cognitive state tracking"""

    @abstractmethod
    def record_execution(
        self,
        session_id: str,
        agent_id: str,
        task: str,
        output: Any,
        tokens_used: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record an agent execution to the ledger.

        Args:
            session_id: Session identifier
            agent_id: Agent that executed
            task: Task description
            output: Agent output
            tokens_used: Tokens consumed
            metadata: Additional execution metadata
        """
        ...

    @abstractmethod
    def update_cognitive_state(
        self, session_id: str, reflection_event: Dict[str, Any]
    ) -> None:
        """
        Update cognitive state with reflection events.

        Args:
            session_id: Session identifier
            reflection_event: Reflection event details (critic feedback, retries, etc.)
        """
        ...

    @abstractmethod
    def get_session_history(self, session_id: str) -> list[Dict[str, Any]]:
        """
        Retrieve session execution history.

        Args:
            session_id: Session identifier

        Returns:
            List of execution records for the session
        """
        ...
