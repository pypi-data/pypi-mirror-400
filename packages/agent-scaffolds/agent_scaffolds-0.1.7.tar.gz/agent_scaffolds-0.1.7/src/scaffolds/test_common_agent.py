"""
Auto-generated scaffold for test_common_agent.
Modify AGENT_DESCRIPTION and configuration fields as needed.
"""

from __future__ import annotations

from typing import Any

from agenthub.interfaces.scaffolds.common_agent import CommonAgentData


AGENT_NAME = 'test_common_agent'
AGENT_DESCRIPTION = 'test_common_agent agent description'

AGENT_ID = None  # Not defined if not synchronized with AgentHub.
MODULE_ID = 'common-agent'
LLM_STRING = 'openai:gpt-5'
PROMPT_FILENAME = 'test_common_agent.prompt'


def _coerce_prompt(prompt_text: str | None) -> str | None:
    if not prompt_text:
        return None

    return prompt_text.strip()


def get_agent_manifest(prompt: str | None = None) -> dict[str, Any]:
    configuration = get_agent_configuration(prompt)
    return {
        "name": AGENT_NAME,
        "avatar_url": None,
        "description": AGENT_DESCRIPTION,
        "module_id": MODULE_ID,
        "configuration": configuration,
    }


def get_agent_configuration(prompt: str | None = None) -> CommonAgentData:
    return CommonAgentData(
        llm=LLM_STRING,
        instructions=_coerce_prompt(prompt) or "'You are an AgentHub agent. Fall back to this instruction when no prompt is provided.'",
        enable_attp=True,
        enable_mcp=False,
        max_iterations=10
    )
