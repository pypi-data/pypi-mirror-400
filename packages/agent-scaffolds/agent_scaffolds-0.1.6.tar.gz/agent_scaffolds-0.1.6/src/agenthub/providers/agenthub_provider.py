from __future__ import annotations

from typing import Any

from ascender.core import Provider
from ascender.core.cli_engine import useCLI

from agenthub.cli.agents import AgentBuilderCLI
from agenthub.cli.copilot import CopilotCLI
from agenthub.configs.main import AgentHubConfig, load_agenthub_config


def provideAgentHub() -> Provider:
    config: AgentHubConfig = load_agenthub_config()
    return [
        {
            "provide": "AGENTHUB_CONFIG",
            "value": config,
        }, 
        useCLI(AgentBuilderCLI), 
        useCLI(CopilotCLI)
    ]
