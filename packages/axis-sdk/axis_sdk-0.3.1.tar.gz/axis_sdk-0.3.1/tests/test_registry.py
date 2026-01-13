"""
Tests for Phase 5 Gate A: Registry Protocols and Definitions
"""
from typing import Dict, List

from axis_sdk.protocols import (
    AgentRegistryProtocol,
    SkillProtocol,
    SkillRegistryProtocol,
)
from axis_sdk.types import AgentDefinition, SkillDefinition


class MockAgentRegistry:
    """Mock implementation for testing protocol compatibility"""

    def get_agent(self, agent_id: str) -> AgentDefinition:
        return AgentDefinition(
            id=agent_id,
            role="tester",
            tier="L1",
            activation_policy="always",
            model="test",
            provider="test",
            budget={"token_budget": 100, "cost_multiplier": 1.0},
            capabilities=[],
            strengths=[],
            weaknesses=[],
            family="test",
            description="test",
            system_prompt="test",
        )

    def list_agents(self) -> List[AgentDefinition]:
        return []


class MockSkillRegistry:
    """Mock implementation for testing protocol compatibility"""

    def get_skill(self, skill_id: str) -> SkillProtocol:
        class MockSkill:
            def execute(self, params: Dict, context: Dict) -> Dict:
                return {"status": "ok"}

        return MockSkill()

    def list_skills(self) -> List[str]:
        return ["test-skill"]


def test_agent_registry_protocol_compliance():
    registry = MockAgentRegistry()
    assert isinstance(registry, AgentRegistryProtocol)


def test_skill_registry_protocol_compliance():
    registry = MockSkillRegistry()
    assert isinstance(registry, SkillRegistryProtocol)


def test_skill_definition_defaults():
    skill = SkillDefinition(
        id="test-skill", name="Test Skill", description="A test skill", version="1.0.0"
    )
    assert skill.schema_version == "1.0.0"
    assert skill.params_schema == {}
    assert skill.output_schema == {}


def test_agent_definition_v1():
    agent = AgentDefinition(
        id="test-agent",
        role="tester",
        tier="L1",
        activation_policy="test",
        model="test",
        provider="test",
        budget={"token_budget": 100, "cost_multiplier": 1.0},
        capabilities=[],
        strengths=[],
        weaknesses=[],
        family="test",
        description="test",
        system_prompt="test",
    )
    assert agent.schema_version == "1.0.0"
