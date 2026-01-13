from typing import Any

from ascender.core import inject
from attp_client import ATTPClient, AttpException, FixedBaseModel
from attp_client.interfaces.objects.agent import IAgentDTO, IAgentResponse
from pydantic import Field
import requests
import re

from agenthub.attp.standalone_tool import tool
from agenthub.configs.main import AgentHubConfig
from agenthub.interfaces.scaffolds.autonomous_agent import AutonomousAgentData
from agenthub.interfaces.scaffolds.common_agent import CommonAgentData
from agenthub.core.scaffolds import ScaffoldEngine, ScaffoldGenerationSpec
from agenthub.interfaces.scaffolds.router_agent import RouterAgentData


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "agent"


def _python_repr(value: str | None) -> str:
    return "None" if value is None else repr(value)


class ConfigSchemaRequest(FixedBaseModel):
    module_id: str


class CreateAgentRequest(FixedBaseModel):
    name: str
    description: str
    module_id: str
    configuration: dict[str, Any]
    avatar_url: str | None = None


class ValidateConfigurationRequest(FixedBaseModel):
    module_id: str
    configuration: dict[str, Any] = Field(description="An agent config you want to validate before creating.")


class ListAgentsRequest(FixedBaseModel):
    search: str | None = None
    page: int
    size: int = 10


class ModifyAgentRequest(FixedBaseModel):
    agent_id: int
    configuration: dict[str, Any]
    name: str | None = None
    description: str | None = None
    avatar_url: str | None = None


class DeleteAgentRequest(FixedBaseModel):
    agent_id: int


class GenerateScaffoldRequest(FixedBaseModel):
    name: str
    description: str | None = None
    module_id: str = "common-agent"
    agent_id: int | None = None
    llm_load_string: str = "openai:gpt-5"
    instruction_template: str | None = None
    avatar_url: str | None = None
    attp_catalog: str | None = None
    prompt_text: str | None = None
    overwrite: bool = False


class CopilotTools:
    def __init__(self, client: ATTPClient) -> None:
        self.client = client
        self.scaffold_engine = ScaffoldEngine()

    async def attach_all(self) -> None:
        await self.config_schema.attach(self.client)
        await self.create_agent.attach(self.client)
        await self.validate_configuration.attach(self.client)
        await self.list_agents.attach(self.client)
        await self.modify_agent.attach(self.client)
        await self.delete_agent.attach(self.client)
        await self.generate_scaffold.attach(self.client)

    @tool("generate_scaffold", "Generate a scaffold file and prompt for an agent.", catalog="agenthub-copilot")
    def generate_scaffold(self, request: GenerateScaffoldRequest) -> dict[str, Any]:
        try:
            spec = ScaffoldGenerationSpec(
                name=request.name,
                description=request.description,
                module_id=request.module_id,
                agent_id=request.agent_id,
                llm_load_string=request.llm_load_string,
                instruction_template=request.instruction_template,
                avatar_url=request.avatar_url,
                attp_catalog=request.attp_catalog,
                prompt_text=request.prompt_text,
                overwrite=request.overwrite,
            )
            result = self.scaffold_engine.generate_scaffold(spec)
            return result
        except FileExistsError as exc:
            raise AttpException("ScaffoldExists", detail={"message": str(exc)}) from exc
        except RuntimeError as exc:
            raise AttpException("ScaffoldModuleNotFound", detail={"message": str(exc)}) from exc

    @tool("config_schema", "Get the configuration schema for an agent module.", catalog="agenthub-copilot")
    def config_schema(self, request: ConfigSchemaRequest) -> dict[str, Any]:
        print(request.module_id)
        match request.module_id:
            case "autonomous-agent":
                schema = AutonomousAgentData.model_json_schema()
                return schema
            case "common-agent":
                schema = CommonAgentData.model_json_schema()
                return schema
            case "route-agent":
                schema = RouterAgentData.model_json_schema()
                return schema
            case _:
                raise AttpException("ModuleIdNotFound", detail={"message": f"Module ID '{request.module_id}' not found."})

    @tool("create_agent", "Create a new agent.", catalog="agenthub-copilot")
    async def create_agent(self, request: CreateAgentRequest) -> IAgentResponse:
        response = await self.client.agents.create_agent(IAgentDTO(
            name=request.name,
            description=request.description,
            module_id=request.module_id,
            configurations=request.configuration,
            avatar_url=request.avatar_url,
        ))
        
        return response

    @tool("validate_configuration", "Validate the configuration for an agent module.", catalog="agenthub-copilot")
    def validate_configuration(self, request: ValidateConfigurationRequest) -> dict[str, Any]:
        match request.module_id:
            case "autonomous-agent":
                try:
                    AutonomousAgentData.model_validate(request.configuration)
                    return {"valid": True}
                except Exception as e:
                    return {"valid": False, "error": str(e)}
            case "common-agent":
                try:
                    CommonAgentData.model_validate(request.configuration)
                    return {"valid": True}
                except Exception as e:
                    return {"valid": False, "error": str(e)}
            case "route-agent":
                try:
                    RouterAgentData.model_validate(request.configuration)
                    return {"valid": True}
                except Exception as e:
                    return {"valid": False, "error": str(e)}
            case _:
                raise AttpException("ModuleIdNotFound", detail={"message": f"Module ID '{request.module_id}' not found."})

    @tool("list_agents", "List autonomous agents.", catalog="agenthub-copilot")
    def list_agents(self, request: ListAgentsRequest) -> dict[str, Any]:
        configs = inject(AgentHubConfig)
        
        agents = requests.get("{}/agents".format(configs.base_url), params={
            "page": request.page,
            "size": request.size,
        }, headers={
            "Authorization": f"Bearer {configs.agt_key}",
        }).json()
        # response = await self.client.agents.get_agents(search=request.search)
        # agents = [
        #     {
        #         "id": agent.id,
        #         "name": agent.name,
        #         "description": agent.description,
        #         "module_id": agent.module_id,
        #         "avatar_url": agent.avatar_url,
        #     }
        #     for agent in response.items
        # ]
        return agents

    @tool("modify_agent", "Modify an existing autonomous agent.", catalog="agenthub-copilot")
    async def modify_agent(self, request: ModifyAgentRequest) -> IAgentResponse:
        agent = await self.client.agents.get_agent(request.agent_id)
        response = await self.client.agents.update_agent(
            agent_id=request.agent_id,
            data=IAgentDTO(
                name=request.name or agent.name,
                description=request.description or agent.description,
                module_id=agent.module_id,
                configurations=request.configuration,
                avatar_url=request.avatar_url,
            )
        )
        return response

    @tool("delete_agent", "Delete an autonomous agent.", catalog="agenthub-copilot")
    async def delete_agent(self, request: DeleteAgentRequest) -> dict[str, Any]:
        await self.client.agents.delete_agent(request.agent_id)
        return {"deleted": True}