from __future__ import annotations

from textwrap import dedent
from typing import Any, Callable

from agenthub.interfaces.scaffold_module import ScaffoldModule


class RouterAgentScaffold(ScaffoldModule):
    module_id = "router-agent"
    name = "Router Agent"
    description = "Router Agent that routes messages to appropriate agents based on their descriptions, optional predefined rules and context."

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

                from agenthub.interfaces.scaffolds.router_agent import RouterAgentData, RouterAgentElement


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


                def get_agent_configuration(prompt: str | None = None) -> RouterAgentData:
                    return RouterAgentData(
                        llm=LLM_STRING,
                        routing_rules=_coerce_prompt(prompt) or None,
                        context_window_size=10,
                        candidate_agents=[],
                        default_agent=RouterAgentElement(agent_id=None, agent_name="please-specify-default-agent"), # NOTE: Do not forget to set a valid default agent!
                        enable_contextual_routing=True,
                    )
                """
            ).strip()
            + "\n"
        )

    def make_prompt_template(self, context: dict[str, Any]) -> str:
        return (
            dedent(
                f"""
                Please route the incoming request to best suited agent based on the given agent descriptions and optional predefined rules.
                """
            ).strip()
            + "\n"
        )

    def load_scaffold(
        self, loader: Callable[[Any | None], dict[str, Any]], agent_id: int | None = None
    ) -> Any:
        return loader(agent_id)
