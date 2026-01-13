from typing import Any
from uuid import UUID
from ascender.common import BaseDTO
from pydantic import Field, field_validator


class RouterAgentElement(BaseDTO):
    agent_id: int | None = Field(..., description="Unique identifier for the autonomous agent")
    agent_name: str | None = Field(None, description="Name of the agent")
    
    @field_validator("agent_id", "agent_name", mode="before")
    def validate_agent_id_or_name(cls, v, info):
        if v is None:
            other_field = "agent_name" if info.field_name == "agent_id" else "agent_id"
            if info.data.get(other_field) is None:
                raise ValueError("Either 'agent_id' or 'agent_name' must be provided.")
        return v


class RouterAgentData(BaseDTO):
    llm: str = Field("openai:gpt-5.1") # Design: 'provider:model' or 'openrouter:auto' for automatic selection
    invoke_configs: dict[str, str] = Field(default_factory=dict) # Additional configurations for
    
    context_window_size: int = Field(10, description="Number of recent messages to consider for routing decisions. (default: 10)")
    
    routing_rules: str | None = Field(None, description="Optional predefined rules for routing decisions.")
    enable_contextual_routing: bool = Field(True, description="Enable contextual analysis for routing decisions based on message content.")
    
    candidate_agents: list[RouterAgentElement] = Field(..., description="List of potential agents to which messages can be routed.")
    default_agent: RouterAgentElement = Field(..., description="Default agent to handle messages that do not match any routing criteria or if routing agent errors out and any other emergency scenarios.")
    
    @field_validator("candidate_agents", mode="after")
    def validate_candidate_agents(cls, v: list[RouterAgentElement], values: Any):
        if not v:
            raise ValueError("At least one candidate agent must be provided.")
        return v