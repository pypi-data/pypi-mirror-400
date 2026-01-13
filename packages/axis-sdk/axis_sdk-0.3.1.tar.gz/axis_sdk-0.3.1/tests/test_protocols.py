"""
Tests for axis-sdk protocols
"""
from axis_sdk.protocols.agent import AgentProtocol, CriticProtocol
from axis_sdk.protocols.orchestrator import ExecutorProtocol, ValidatorProtocol


class MockAgent:
    """Mock implementation of AgentProtocol"""

    def __init__(self, agent_id: str):
        self._agent_id = agent_id

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def validate_invocation(self, context: dict) -> bool:
        return True

    def run(self, task: str, context: dict) -> tuple:
        return True, "success", 100, {}


class MockCritic:
    """Mock implementation of CriticProtocol"""

    def evaluate(self, output, context: dict) -> tuple:
        return True, "Passed", 1.0


class MockExecutor:
    """Mock implementation of ExecutorProtocol"""

    def execute(self, agent_id: str, task: str, session_id: str) -> tuple:
        return True, "executed", 50


class MockValidator:
    """Mock implementation of ValidatorProtocol"""

    def get_contract(self, agent_id: str):
        return {"id": agent_id}

    def validate_pre_conditions(self, agent_id: str, context: dict) -> bool:
        return True

    def validate_post_conditions(self, agent_id: str, output, context: dict) -> bool:
        return True


def test_agent_protocol_compliance():
    """Test that mock agent implements AgentProtocol"""
    agent = MockAgent("test_agent")
    assert isinstance(agent, AgentProtocol)
    assert agent.agent_id == "test_agent"
    assert agent.validate_invocation({})
    success, output, tokens, metadata = agent.run("task", {})
    assert success is True


def test_critic_protocol_compliance():
    """Test that mock critic implements CriticProtocol"""
    critic = MockCritic()
    assert isinstance(critic, CriticProtocol)
    passed, feedback, score = critic.evaluate("output", {})
    assert passed is True
    assert score == 1.0


def test_executor_protocol_compliance():
    """Test that mock executor implements ExecutorProtocol"""
    executor = MockExecutor()
    assert isinstance(executor, ExecutorProtocol)
    success, output, tokens = executor.execute("agent", "task", "session")
    assert success is True


def test_validator_protocol_compliance():
    """Test that mock validator implements ValidatorProtocol"""
    validator = MockValidator()
    assert isinstance(validator, ValidatorProtocol)
    assert validator.get_contract("agent") is not None
    assert validator.validate_pre_conditions("agent", {}) is True
    assert validator.validate_post_conditions("agent", "output", {}) is True
