"""
Reasoning Types

Structured types for orchestration, routing, and policy decisions.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OrchestrationRequest(BaseModel):
    """Request for orchestration"""

    query: str = Field(..., description="User query or task description")
    session_id: str = Field(..., description="Session identifier")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Execution context"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional constraints (budget, timeout, etc.)"
    )


class OrchestrationResult(BaseModel):
    """Result of orchestration"""

    agent_id: str = Field(..., description="Agent that executed")
    success: bool = Field(..., description="Execution success flag")
    output: Any = Field(..., description="Agent output")
    tokens_used: int = Field(default=0, description="Tokens consumed")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Execution metadata"
    )


class RoutingDecision(BaseModel):
    """Structured routing decision"""

    agent_id: str = Field(..., description="Selected agent ID")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )
    reasoning: str = Field(..., description="Why this agent was selected")
    alternatives: List[str] = Field(
        default_factory=list, description="Alternative agent candidates"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Routing-specific metadata"
    )


class PolicyDecision(BaseModel):
    """Structured policy evaluation decision"""

    policy_id: str = Field(..., description="Policy that was evaluated")
    allowed: bool = Field(..., description="Whether action is allowed")
    reasoning: str = Field(..., description="Why this decision was made")
    constraints: Optional[Dict[str, Any]] = Field(
        default=None, description="Applied constraints (rate limits, quotas, etc.)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Policy-specific metadata"
    )
