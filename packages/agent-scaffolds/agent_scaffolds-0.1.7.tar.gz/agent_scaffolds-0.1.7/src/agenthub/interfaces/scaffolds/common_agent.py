from typing import Any
from uuid import UUID
from ascender.common import BaseDTO
from pydantic import Field


class CommonAgentData(BaseDTO):
    llm: str = Field("openai:gpt-5.1") # Design: 'provider:model' or 'openrouter:auto' for automatic selection
    invoke_configs: dict[str, Any] = Field(default_factory=dict) # Additional configurations for LLM invocation
    instructions: str = Field(..., description="High-level instructions guiding the agent's behavior (basically, its system prompt.)")
    max_iterations: int = Field(10, description="Maximum number of iterations the agent can perform")
    
    enable_attp: bool = Field(True, description="Flag to enable or disable ATTP tool usage")
    enable_mcp: bool = Field(False, description="Flag to enable or disable MCP tool usage")
    
    attp_catalogs: list[str] = Field(default_factory=list, description="List of ATTP tool catalogs the agent can use")
    mcp_catalogs: list[str] = Field(default_factory=list, description="List of MCP tool catalogs the agent can use")