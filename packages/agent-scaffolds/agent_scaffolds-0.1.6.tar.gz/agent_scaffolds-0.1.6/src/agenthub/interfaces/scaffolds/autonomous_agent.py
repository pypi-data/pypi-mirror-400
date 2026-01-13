from ascender.common import BaseDTO


from typing import Any
from uuid import UUID
from ascender.common import BaseDTO
from pydantic import Field


class IAgentInstructionDTO(BaseDTO):
    objective: str = Field(..., description="Primary objective or goal for the autonomous agent to achieve.")
    role: str | None = Field(None, description="Role or persona the agent should adopt while interacting.")
    backstory: str | None = Field(None, description="Background story or context for the agent's behavior.")
    constraints: list[str] = Field(default_factory=list, description="List of constraints or rules the agent must adhere to. Hard constraints that must not be violated.")
    preferences: list[str] = Field(default_factory=list, description="List of preferences or guidelines for the agent's actions. Soft preferences that can be considered but may be overridden if necessary.")
    output_format: str | None = Field(None, description="Expected output format (json, markdown, bullets, etc.) for the agent's responses.")
    
    @staticmethod
    def from_yaml(yaml_str: str) -> 'IAgentInstructionDTO':
        import yaml
        data = yaml.safe_load(yaml_str)
        return IAgentInstructionDTO(**data)


class AutonomousAgentData(BaseDTO):
    llm: str = Field("openai:gpt-5.1") # Design: 'provider:model' or 'openrouter:auto' for automatic selection
    invoke_configs: dict[str, Any] = Field(default_factory=dict) # Additional configurations for LLM invocation
    allowed_states: list[str] = Field(default_factory=lambda: ["thinking", "acting"]) # e.g. ['thinking', 'acting']
    policies: list[str] = Field(default_factory=lambda: ["think_before_acting", "minimize_tool_calls", "see_own_tokens", "prefer_fast_llm", "avoid_expensive_llm"]) # e.g. ['think_before_acting', 'minimize_tool_calls', 'see_own_tokens', 'prefer_fast_llm', 'avoid_expensive_llm']
    enabled_filters: list[str] = Field(default_factory=lambda: ["empty_response_regenerate"]) # e.g. ['profanity_filter', 'safety_filter', 'empty_response_regenerate]
    
    instructions: IAgentInstructionDTO = Field(...) # Instructions for the autonomous agent
    
    enable_attp: bool = True # Enable ATTP protocol for tool calls
    enable_mcp: bool = True  # Enable MCP protocol for tool calls
    enable_http: bool = False # Enable HTTP protocol for tool calls
    
    attp_catalogs: list[str] = Field(default_factory=list) # List of ATTP catalogs available to the agent
    mcp_catalogs: list[str] = Field(default_factory=list)  # List of MCP catalogs available to the agent
    
    tool_execution_error: str = "An error {error} occurred while trying to use the tool. Please try again later." # Error message template for tool execution errors
    
    sign_metadata: bool = True # Sign LLM response message with metadata (containing state and model that was used)