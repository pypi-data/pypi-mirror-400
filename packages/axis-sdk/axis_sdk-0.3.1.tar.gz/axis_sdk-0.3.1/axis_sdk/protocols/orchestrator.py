"""
Orchestrator Contracts

Defines the interface between orchestration layer and execution runtime.
"""
from abc import abstractmethod
from typing import Any, Dict, Optional, Protocol, Tuple, runtime_checkable


@runtime_checkable
class ExecutorProtocol(Protocol):
    """Interface for task execution backends"""

    @abstractmethod
    def execute(
        self, agent_id: str, task: str, session_id: str
    ) -> Tuple[bool, Any, int]:
        """
        Execute a task via an agent.

        Args:
            agent_id: Which agent to use
            task: Task description
            session_id: Session identifier for tracking

        Returns:
            Tuple of (success, output, tokens_used)
        """
        ...


@runtime_checkable
class ValidatorProtocol(Protocol):
    """Interface for contract validation"""

    @abstractmethod
    def get_contract(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve contract definition for an agent"""
        ...

    @abstractmethod
    def validate_pre_conditions(self, agent_id: str, context: Dict[str, Any]) -> bool:
        """Validate preconditions before execution"""
        ...

    @abstractmethod
    def validate_post_conditions(
        self, agent_id: str, output: Any, context: Dict[str, Any]
    ) -> bool:
        """Validate postconditions after execution"""
        ...
