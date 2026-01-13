"""
Auto-generated scaffold for agent-creation-copilot.
Modify AGENT_DESCRIPTION and configuration fields as needed.
"""

from __future__ import annotations

from typing import Any

from agenthub.interfaces.scaffolds.autonomous_agent import (
    AutonomousAgentData,
    IAgentInstructionDTO,
)


AGENT_NAME = 'agent-creation-copilot'
AGENT_DESCRIPTION = 'agent-creation-copilot agent description'

AGENT_ID = 4  # Not defined if not synchronized with AgentHub.
MODULE_ID = 'autonomous-agent'
LLM_STRING = 'openai:gpt-4o'
PROMPT_FILENAME = 'agent_creation_copilot.prompt'


def _coerce_prompt(prompt_text: str | None) -> IAgentInstructionDTO | None:
    if not prompt_text:
        return None

    cleaned = "\n".join(
        line for line in prompt_text.splitlines()
        if not line.lstrip().startswith("//")
    )
    return IAgentInstructionDTO.from_yaml(cleaned)


def get_agent_manifest(prompt: str | None = None) -> dict[str, Any]:
    configuration = get_agent_configuration(prompt)
    return {
        "name": AGENT_NAME,
        "avatar_url": None,
        "description": AGENT_DESCRIPTION,
        "module_id": MODULE_ID,
        "configuration": configuration,
    }


def get_agent_configuration(prompt: str | None = None) -> AutonomousAgentData:
    instructions = _coerce_prompt(prompt) or IAgentInstructionDTO(
        objective='You are an AgentHub agent. Fall back to this instruction when no prompt is provided.',
        role=None,
        backstory=None,
        constraints=[],
        preferences=[],
        output_format="json",
    )
    return AutonomousAgentData(
        llm=LLM_STRING,
        instructions=instructions,
        policies=["think_before_acting", "see_own_tokens"],
        attp_catalogs=["agenthub-copilot"],
        # enable_attp=False,
        # enable_mcp=False
    )
