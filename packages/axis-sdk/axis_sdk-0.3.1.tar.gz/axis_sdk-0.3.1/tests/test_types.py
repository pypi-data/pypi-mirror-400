"""
Tests for axis-sdk type definitions
"""
import pytest
from axis_sdk.types.agent import (
    AgentDefinition,
    BudgetConfig,
    GovernanceConfig,
    SemanticProfile,
)
from pydantic import ValidationError


def test_budget_config_valid():
    """Test valid BudgetConfig creation"""
    config = BudgetConfig(token_budget=1000, cost_multiplier=1.5)
    assert config.token_budget == 1000
    assert config.cost_multiplier == 1.5


def test_semantic_profile_defaults():
    """Test SemanticProfile with default values"""
    profile = SemanticProfile(cognitive_cost_estimate="low")
    assert profile.when_to_invoke == []
    assert profile.prerequisite_states == []
    assert profile.expected_output_schema == {
        "format": "markdown",
        "structure": "answer",
    }


def test_semantic_profile_invalid_cost():
    """Test SemanticProfile rejects invalid cost estimate"""
    with pytest.raises(ValidationError):
        SemanticProfile(cognitive_cost_estimate="invalid")


def test_agent_definition_complete():
    """Test complete AgentDefinition"""
    agent = AgentDefinition(
        id="test_agent",
        role="analyst",
        tier="L1",
        activation_policy="on_demand",
        model="gpt-4",
        provider="openai",
        budget=BudgetConfig(token_budget=5000, cost_multiplier=1.0),
        capabilities=["analysis"],
        strengths=["fast"],
        weaknesses=["expensive"],
        family="gpt",
        description="Test agent",
        system_prompt="You are a test",
    )
    assert agent.id == "test_agent"
    assert agent.budget.token_budget == 5000


def test_governance_config_defaults():
    """Test GovernanceConfig with defaults"""
    config = GovernanceConfig(
        linked_contract="contract.yml",
        update_ledger="ledger.db",
        session_tracker="tracker.db",
    )
    assert config.lineage_verification is True
    assert config.contract_enforced is True
    assert config.checksum_verification is True
