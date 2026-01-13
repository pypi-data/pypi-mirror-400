"""
Reasoning Protocols

Orchestration, routing, and policy evaluation interfaces.
"""
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Protocol, runtime_checkable

if TYPE_CHECKING:
    from axis_sdk.protocols.skills import SkillProtocol

from axis_sdk.types.agent import AgentDefinition
from axis_sdk.types.reasoning import (
    OrchestrationRequest,
    OrchestrationResult,
    PolicyDecision,
    RoutingDecision,
)


@runtime_checkable
class OrchestratorProtocol(Protocol):
    """Core orchestration interface"""

    @abstractmethod
    def orchestrate(self, request: OrchestrationRequest) -> OrchestrationResult:
        """
        Orchestrate a request through the system.

        Args:
            request: Orchestration request with query and context

        Returns:
            Orchestration result with agent output and metadata
        """
        ...


@runtime_checkable
class RouterProtocol(Protocol):
    """Semantic routing interface"""

    @abstractmethod
    def route(self, query: str, context: Dict[str, Any]) -> RoutingDecision:
        """
        Route a query to an appropriate agent.

        Args:
            query: User query or task description
            context: Execution context

        Returns:
            RoutingDecision with selected agent and confidence
        """
        ...


@runtime_checkable
class PolicyEngineProtocol(Protocol):
    """Policy evaluation interface"""

    @abstractmethod
    def evaluate_policy(
        self, policy_id: str, context: Dict[str, Any]
    ) -> PolicyDecision:
        """
        Evaluate a policy against context.

        Args:
            policy_id: Policy identifier
            context: Evaluation context

        Returns:
            PolicyDecision with allow/deny and reasoning
        """
        ...


@runtime_checkable
class AgentRegistryProtocol(Protocol):
    """
    Read-only protocol for agent discovery.
    """

    @abstractmethod
    def get_agent(self, agent_id: str) -> AgentDefinition:
        """Retrieve agent definition by ID."""
        ...

    @abstractmethod
    def list_agents(self) -> List[AgentDefinition]:
        """List all available agent definitions."""
        ...


@runtime_checkable
class SkillRegistryProtocol(Protocol):
    """
    Read-only protocol for skill discovery.
    """

    @abstractmethod
    def get_skill(self, skill_id: str) -> "SkillProtocol":
        """Retrieve skill implementation by ID."""
        ...

    @abstractmethod
    def list_skills(self) -> List[str]:
        """List all available skill IDs."""
        ...
