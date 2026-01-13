"""
Shared Type Definitions

Stable types used across AXIS components.
Based on Pydantic for validation.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BudgetConfig(BaseModel):
    """Token budget configuration"""

    token_budget: int
    cost_multiplier: float


class SemanticProfile(BaseModel):
    """Semantic activation profile for agents"""

    when_to_invoke: List[str] = Field(
        default_factory=list, description="Intent triggers for agent activation"
    )
    cognitive_cost_estimate: str = Field(..., pattern="^(low|medium|high|critical)$")
    prerequisite_states: List[str] = Field(default_factory=list)
    expected_output_schema: Dict[str, str] = Field(
        default_factory=lambda: {"format": "markdown", "structure": "answer"}
    )


class AgentDefinition(BaseModel):
    """
    Complete agent definition schema.

    This is the canonical structure for agent metadata.
    """

    id: str
    role: str
    tier: str
    activation_policy: str
    model: str
    provider: str
    budget: BudgetConfig
    capabilities: List[str]
    strengths: List[str]
    weaknesses: List[str]
    family: str
    description: str
    system_prompt: str
    semantic_profile: Optional[SemanticProfile] = None
    schema_version: str = "1.0.0"


class SkillDefinition(BaseModel):
    """
    Metadata for a skill.
    """

    id: str
    name: str
    description: str
    version: str
    schema_version: str = "1.0.0"
    params_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GovernanceConfig(BaseModel):
    """Governance enforcement configuration"""

    linked_contract: str
    update_ledger: str
    session_tracker: str
    lineage_verification: bool = True
    contract_enforced: bool = True
    checksum_verification: bool = True
