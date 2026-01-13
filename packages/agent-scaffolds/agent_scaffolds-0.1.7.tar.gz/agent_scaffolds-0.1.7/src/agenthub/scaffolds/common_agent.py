from __future__ import annotations

from textwrap import dedent
from typing import Any, Callable

from agenthub.interfaces.scaffold_module import ScaffoldModule


class CommonAgentScaffold(ScaffoldModule):
    module_id = "common-agent"
    name = "Common Agent"
    description = "Commonly used agent scaffold."

    def generate_manifest(self, context: dict[str, Any]) -> str:
        agent_id = context.get("agent_id")
        agent_id_repr = "None" if agent_id is None else str(agent_id)
        agent_name_repr = context["agent_name_repr"]
        description_repr = context["description_repr"]
        module_id_repr = context["module_id_repr"]
        llm_load_string_repr = context["llm_load_string_repr"]
        prompt_filename_repr = context["prompt_filename_repr"]
        instruction_template_repr = context["instruction_template_repr"]
        avatar_url_repr = context["avatar_url_repr"]

        return (
            dedent(
                f"""
                \"\"\"
                Auto-generated scaffold for {context['agent_name']}.
                Modify AGENT_DESCRIPTION and configuration fields as needed.
                \"\"\"

                from __future__ import annotations

                from typing import Any

                from agenthub.interfaces.scaffolds.common_agent import CommonAgentData


                AGENT_NAME = {agent_name_repr}
                AGENT_DESCRIPTION = {description_repr}

                AGENT_ID = {agent_id_repr}  # Not defined if not synchronized with AgentHub.
                MODULE_ID = {module_id_repr}
                LLM_STRING = {llm_load_string_repr}
                PROMPT_FILENAME = {prompt_filename_repr}


                def _coerce_prompt(prompt_text: str | None) -> str | None:
                    if not prompt_text:
                        return None

                    return prompt_text.strip()


                def get_agent_manifest(prompt: str | None = None) -> dict[str, Any]:
                    configuration = get_agent_configuration(prompt)
                    return {{
                        \"name\": AGENT_NAME,
                        \"avatar_url\": {avatar_url_repr},
                        \"description\": AGENT_DESCRIPTION,
                        \"module_id\": MODULE_ID,
                        \"configuration\": configuration,
                    }}


                def get_agent_configuration(prompt: str | None = None) -> CommonAgentData:
                    return CommonAgentData(
                        llm=LLM_STRING,
                        instructions=_coerce_prompt(prompt) or "{instruction_template_repr}",
                        enable_attp=True,
                        enable_mcp=False,
                        max_iterations=10
                    )
                """
            ).strip()
            + "\n"
        )

    def make_prompt_template(self, context: dict[str, Any]) -> str:
        agent_name = context.get("agent_name", "the agent")
        return (
            dedent(
                f"""
                You are helpful AI assistant {agent_name}.
                Follow the user's instructions carefully and provide the best possible response.
                If you are unsure about any aspect of the instructions, ask for clarification.
                Always aim to be clear, concise, and informative in your responses.
                """
            ).strip()
            + "\n"
        )

    def load_scaffold(
        self, loader: Callable[[Any | None], dict[str, Any]], agent_id: int | None = None
    ) -> Any:
        return loader(agent_id)
