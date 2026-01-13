"""
Runtime and governance protocol definitions.
"""
from abc import abstractmethod
from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class AuthorityProvider(Protocol):
    """Provider for governance authority levels."""

    @abstractmethod
    def get_authority_level(self, context: Any) -> str:
        """Get authority level for context.

        Returns:
            str: Authority level (e.g., 'APPROVED', 'BLOCKED', 'WARN')
        """
        ...


@runtime_checkable
class RuntimeExecutor(Protocol):
    """Executor for runtime task execution."""

    @abstractmethod
    def execute_runtime(self, task: str, context: Any) -> Any:
        """Execute runtime task.

        Args:
            task: Task identifier
            context: Execution context

        Returns:
            Any: Task result
        """
        ...


@runtime_checkable
class EpistemologyStore(Protocol):
    """Store for epistemological knowledge."""

    @abstractmethod
    def get_epistemology(self, key: str) -> Dict[str, Any]:
        """Retrieve epistemology entry.

        Args:
            key: Knowledge key

        Returns:
            Dict containing epistemology data
        """
        ...
