# AXIS SDK

**Version:** 0.3.0
**Status:** Production Ready
**License:** MIT

## Purpose

The `axis-sdk` is a **zero-dependency boundary layer** that defines contracts between AXIS components.

### ✅ Included
- Protocol definitions (`typing.Protocol`)
- Type definitions (`pydantic.BaseModel`)
- Interface contracts for:
  - Agents (`AgentProtocol`)
  - Orchestrators (`OrchestratorProtocol`)
  - Telemetry (`TelemetryProtocol`)
  - Ledger (`LedgerProtocol`)
  - Skills (`SkillProtocol`)
  - Reasoning (`ReasoningProtocol`)

### ❌ Excluded
- Business logic
- Runtime implementations
- Side effects (I/O, network, database)
- External dependencies (except `pydantic` for validation)

## Installation

```bash
pip install axis-sdk
```

## Quick Start

```python
from axis_sdk.protocols import AgentProtocol
from axis_sdk.types import AgentConfig

# Define your agent implementing the protocol
class MyAgent:
    """Custom agent implementation."""

    def __init__(self, config: AgentConfig):
        self.config = config

    @property
    def agent_id(self) -> str:
        return self.config.agent_id

    def validate_invocation(self, context: dict) -> bool:
        """Validate if agent can handle this invocation."""
        return True

    def run(self, task: str, context: dict) -> tuple:
        """Execute the agent task."""
        result = {"status": "completed", "output": "Task done"}
        tokens_used = 150
        metadata = {"model": "gemini-2.0-flash"}
        return True, result, tokens_used, metadata
```

## API Reference

### Protocols

#### AgentProtocol
```python
from axis_sdk.protocols import AgentProtocol

@runtime_checkable
class AgentProtocol(Protocol):
    @property
    def agent_id(self) -> str: ...

    def validate_invocation(self, context: Dict[str, Any]) -> bool: ...

    def run(self, task: str, context: Dict[str, Any]) -> Tuple[bool, Any, int, Dict]: ...
```

#### OrchestratorProtocol
```python
from axis_sdk.protocols import OrchestratorProtocol

@runtime_checkable
class OrchestratorProtocol(Protocol):
    def route_task(self, task: str, context: Dict[str, Any]) -> str: ...

    def execute_agent(self, agent_id: str, task: str, context: Dict[str, Any]) -> Dict: ...
```

### Types

#### AgentConfig
```python
from axis_sdk.types import AgentConfig

config = AgentConfig(
    agent_id="my-agent",
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=1000
)
```

## Development

### Install Dev Dependencies
```bash
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest
```

### Run Linter
```bash
ruff check axis_sdk
```

### Run Type Checker
```bash
mypy axis_sdk
```

## License

MIT License - See [LICENSE](LICENSE) file.

## Links

- **GitHub:** https://github.com/emilyveigaai/axis-sdk
- **PyPI:** https://pypi.org/project/axis-sdk/
- **Issues:** https://github.com/emilyveigaai/axis-sdk/issues
- **Documentation:** https://github.com/emilyveigaai/axis-sdk#readme

---

**Part of AXIS Migration Project**
Separated from monorepo: https://github.com/emilyveigaai/AXIS
