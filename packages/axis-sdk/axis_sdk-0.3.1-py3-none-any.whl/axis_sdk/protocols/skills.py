"""
Skill Protocols

Defines how skills are invoked and matched.
"""
from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class SkillProtocol(Protocol):
    """
    Protocol for executable skills.

    A skill is a discrete capability that can be invoked by an agent.
    """

    def execute(
        self, params: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the skill with provided parameters.

        Args:
            params: Parameters specific to the skill logic.
            context: Global execution context (session, telemetry info).

        Returns:
            Dict containing execution results and status.
        """
        ...
