from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from importlib import resources


# When used as a library, write scaffolds into the caller's working directory.
SCAFFOLDS_DIR = Path.cwd() / "scaffolds"
TEMPLATES_PACKAGE = "agenthub.copilot.templates"


@dataclass(frozen=True)
class CopilotScaffoldSpec:
    agent_name: str = "agent-creation-copilot"
    description: str = "agent-creation-copilot agent description"
    agent_id: int | None = 4
    module_id: str = "autonomous-agent"
    llm_string: str = "openai:gpt-5.1"
    prompt_filename: str = "agent_creation_copilot.prompt"


class AgentCreationCopilotSDK:
    def __init__(self, spec: CopilotScaffoldSpec | None = None) -> None:
        self.spec = spec or CopilotScaffoldSpec()

    def render_scaffold(self) -> str:
        agent_id_repr = "None" if self.spec.agent_id is None else str(self.spec.agent_id)
        return (
            dedent(
                f"""
                \"\"\"
                Auto-generated scaffold for {self.spec.agent_name}.
                Modify AGENT_DESCRIPTION and configuration fields as needed.
                \"\"\"

                from __future__ import annotations

                from typing import Any

                from agenthub.interfaces.scaffolds.autonomous_agent import (
                    AutonomousAgentData,
                    IAgentInstructionDTO,
                )


                AGENT_NAME = {self.spec.agent_name!r}
                AGENT_DESCRIPTION = {self.spec.description!r}

                AGENT_ID = {agent_id_repr}  # Not defined if not synchronized with AgentHub.
                MODULE_ID = {self.spec.module_id!r}
                LLM_STRING = {self.spec.llm_string!r}
                PROMPT_FILENAME = {self.spec.prompt_filename!r}


                def _coerce_prompt(prompt_text: str | None) -> IAgentInstructionDTO | None:
                    if not prompt_text:
                        return None

                    cleaned = "\\n".join(
                        line for line in prompt_text.splitlines()
                        if not line.lstrip().startswith("//")
                    )
                    return IAgentInstructionDTO.from_yaml(cleaned)


                def get_agent_manifest(prompt: str | None = None) -> dict[str, Any]:
                    configuration = get_agent_configuration(prompt)
                    return {{
                        "name": AGENT_NAME,
                        "avatar_url": None,
                        "description": AGENT_DESCRIPTION,
                        "module_id": MODULE_ID,
                        "configuration": configuration,
                    }}


                def get_agent_configuration(prompt: str | None = None) -> AutonomousAgentData:
                    instructions = _coerce_prompt(prompt) or IAgentInstructionDTO(
                        objective="You are an AgentHub agent. Fall back to this instruction when no prompt is provided.",
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
                    )
                """
            ).strip()
            + "\n"
        )

    def render_prompt(self) -> str:
        prompt_path = resources.files(TEMPLATES_PACKAGE) / self.spec.prompt_filename
        return prompt_path.read_text(encoding="utf-8")

    def scaffold_paths(self) -> tuple[Path, Path]:
        scaffold_path = SCAFFOLDS_DIR / "agent_creation_copilot.py"
        prompt_path = scaffold_path.with_suffix(".prompt")
        return scaffold_path, prompt_path

    def write_scaffold(self, overwrite: bool = False) -> tuple[Path, Path]:
        scaffold_path, prompt_path = self.scaffold_paths()
        if (scaffold_path.exists() or prompt_path.exists()) and not overwrite:
            raise FileExistsError("Scaffold already exists. Use overwrite=True to replace it.")

        SCAFFOLDS_DIR.mkdir(parents=True, exist_ok=True)
        scaffold_path.write_text(self.render_scaffold().rstrip() + "\n", encoding="utf-8")
        prompt_path.write_text(self.render_prompt().rstrip() + "\n", encoding="utf-8")
        return scaffold_path, prompt_path
