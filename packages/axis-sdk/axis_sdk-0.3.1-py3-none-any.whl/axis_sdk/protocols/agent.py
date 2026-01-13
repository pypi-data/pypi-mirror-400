"""
Agent Protocol Definitions

Pure interface definitions for AXIS agents.
No runtime logic, no side effects.
"""
from abc import abstractmethod
from typing import Any, Dict, Protocol, Tuple, runtime_checkable


@runtime_checkable
class AgentProtocol(Protocol):
    """
    Core interface that all AXIS agents must implement.

    This is a structural protocol - any class implementing these methods
    is compatible, regardless of inheritance.
    """

    @property
    def agent_id(self) -> str:
        """Unique identifier for this agent"""
        ...

    @abstractmethod
    def validate_invocation(self, context: Dict[str, Any]) -> bool:
        """
        Check if the agent can be invoked in the given context.

        Args:
            context: Execution context including session info

        Returns:
            True if agent can proceed, False otherwise
        """
        ...

    @abstractmethod
    def run(
        self, task: str, context: Dict[str, Any]
    ) -> Tuple[bool, Any, int, Dict[str, Any]]:
        """
        Execute the agent's primary task.

        Args:
            task: Task description or prompt
            context: Execution context

        Returns:
            Tuple of (success, output, tokens_used, metadata)
        """
        ...


@runtime_checkable
class CriticProtocol(Protocol):
    """Interface for critic/validation components"""

    @abstractmethod
    def evaluate(self, output: Any, context: Dict[str, Any]) -> Tuple[bool, str, float]:
        """
        Evaluate agent output.

        Args:
            output: The agent's output to evaluate
            context: Execution context

        Returns:
            Tuple of (passed, feedback, score)
        """
        ...
