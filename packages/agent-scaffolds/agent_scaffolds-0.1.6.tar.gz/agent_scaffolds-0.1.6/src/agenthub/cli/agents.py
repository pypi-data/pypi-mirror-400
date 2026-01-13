"""Agent scaffold management CLI."""

from __future__ import annotations

import importlib.util
import importlib.resources as resources
import inspect
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, cast

from ascender.core.cli_engine import Command, GenericCLI, Handler, Parameter
from attp_client import CorrelatedRPCException, NotFoundError
from attp_client.client import ATTPClient
from attp_client.interfaces.objects.agent import IAgentDTO, IAgentResponse
from attp_core.rs_api import Limits
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from agenthub.configs.main import AgentHubConfig, load_agenthub_config
from agenthub.interfaces.scaffold_module import ScaffoldModule
from agenthub.core.scaffolds import ScaffoldEngine, ScaffoldGenerationSpec


PROJECT_ROOT = Path.cwd()
SRC_DIR = PROJECT_ROOT


@dataclass(slots=True)
class AgentScaffold:
    slug: str
    name: str
    manifest_loader: Callable[[str | None], dict[str, Any]]
    path: Path
    prompt_path: Path
    module_id: str
    description: str
    agent_id: int | None

    def load_manifest(self, prompt_override: str | None) -> dict[str, Any]:
        return self.manifest_loader(prompt_override)


@dataclass(slots=True)
class ScaffoldModuleSpec:
    module_id: str
    name: str
    description: str
    instance: ScaffoldModule
    path: Path


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "agent"


def _python_repr(value: str | None) -> str:
    return "None" if value is None else repr(value)


def _load_scaffold(module_path: Path) -> AgentScaffold:
    module_name = f"scaffolds.{module_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Unable to load scaffold module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    agent_name = getattr(module, "AGENT_NAME", module_path.stem)
    agent_id = getattr(module, "AGENT_ID", None)
    manifest_loader = getattr(module, "get_agent_manifest", None)

    if not callable(manifest_loader):
        raise RuntimeError(f"Scaffold {module_path} is missing get_agent_manifest")

    manifest = cast(dict[str, Any], manifest_loader(None))
    module_id = manifest.get("module_id", "rpc-agent")
    description = manifest.get("description", "")

    return AgentScaffold(
        slug=module_path.stem,
        name=agent_name,
        manifest_loader=cast(Callable[[str | None], dict[str, Any]], manifest_loader),
        path=module_path,
        prompt_path=module_path.with_suffix(".prompt"),
        module_id=module_id,
        description=description,
        agent_id=agent_id,
    )


@Command(name="agents", description="AgentHub agent builder CLI")
class AgentBuilderCLI(GenericCLI):
    """Utility commands for working with AgentHub scaffolds."""

    def __init__(self) -> None:
        super().__init__()
        self.console = Console()
        self.project_root = PROJECT_ROOT
        self.scaffolds_dir = PROJECT_ROOT / "scaffolds"
        self.scaffold_engine = ScaffoldEngine(self.scaffolds_dir)
        self.scaffold_modules = self._discover_scaffold_modules()
        self.settings: AgentHubConfig = load_agenthub_config()

    @Handler("new", description="Create a new AgentHub agent scaffold")
    async def create_agent_scaffold(
        self,
        name: str = Parameter(description="AgentHub agent name (will be slugified for files)", names=["name"]),
        description: str | None = Parameter(
            None,
            description="Agent description",
            names=["-d", "--description"],
        ),
        module_id: str = Parameter(
            "common-agent",
            description="AgentHub module id",
            names=["-m", "--module"],
        ),
        agent_id: int | None = Parameter(
            None,
            description="Expected AgentHub ID",
            names=["-i", "--id"],
        ),
        llm_load_string: str = Parameter(
            "openai:gpt-5",
            description="LLM load string for RPCAgentData",
            names=["--llm"],
        ),
        instruction_template: str | None = Parameter(
            None,
            description="Fallback instruction template if prompt is empty",
            names=["--instruction"],
        ),
        avatar_url: str | None = Parameter(
            None,
            description="Optional avatar URL",
            names=["--avatar"],
        ),
        attp_catalog: str | None = Parameter(
            None,
            description="Optional ATTP catalog name",
            names=["--catalog"],
        ),
        enable_tables_reading: bool = Parameter(
            False,
            description="Enable tables reading mode",
            names=["--tables"],
        ),
        enable_attp: bool = Parameter(
            True,
            description="Control ATTP integration flag",
            names=["--attp"],
        ),
        overwrite: bool = Parameter(
            False,
            description="Overwrite scaffold if it already exists",
            names=["-f", "--force"],
        ),
    ) -> None:
        slug = _slugify(name)
        scaffold_path = self.scaffolds_dir / f"{slug}.py"
        prompt_path = scaffold_path.with_suffix(".prompt")

        if scaffold_path.exists() and not overwrite:
            if not Confirm.ask(f"{scaffold_path.name} exists. Overwrite?"):
                self.console.print("[yellow]Aborted - existing files left untouched.[/yellow]")
                return

        module_spec = self.scaffold_modules.get(module_id)
        if not module_spec:
            available = ", ".join(sorted(self.scaffold_modules.keys()))
            self.console.print(f"[red]Unknown module '{module_id}'.[/red]")
            if available:
                self.console.print(f"[yellow]Available modules:[/yellow] {available}")
            return

        description = description or f"{name} agent description"
        instruction_template = instruction_template or (
            "You are an AgentHub agent. Fall back to this instruction when no prompt is provided."
        )

        context = {
            "agent_name": name,
            "agent_name_repr": repr(name),
            "agent_id": agent_id,
            "description_repr": repr(description),
            "module_id": module_id,
            "module_id_repr": repr(module_id),
            "llm_load_string_repr": repr(llm_load_string),
            "prompt_filename_repr": repr(prompt_path.name),
            "instruction_template_repr": repr(instruction_template),
            "avatar_url_repr": _python_repr(avatar_url),
            "attp_catalog_repr": _python_repr(attp_catalog),
            "enable_attp": enable_attp,
            "enable_tables_reading": enable_tables_reading,
        }

        prompt_default = module_spec.instance.make_prompt_template(context)
        prompt_text = Prompt.ask("Prompt text", default=prompt_default)

        gen_spec = ScaffoldGenerationSpec(
            name=name,
            description=description,
            module_id=module_id,
            agent_id=agent_id,
            llm_load_string=llm_load_string,
            instruction_template=instruction_template,
            avatar_url=avatar_url,
            attp_catalog=attp_catalog,
            prompt_text=prompt_text,
            overwrite=overwrite,
            scaffolds_dir=self.scaffolds_dir,
        )

        self.scaffold_engine.generate_scaffold(gen_spec)

        self.console.print(
            f"[green]Scaffold created:[/green] {scaffold_path.relative_to(self.project_root)}"
        )
        self.console.print(
            f"[green]Prompt created:[/green] {prompt_path.relative_to(self.project_root)}"
        )

    @Handler("status", description="Show local scaffold state compared to AgentHub")
    async def show_status(self) -> None:
        scaffolds = self._discover_scaffolds()
        if not scaffolds:
            self.console.print("[yellow]No agent scaffolds found.[/yellow]")
            return

        table = Table(title="AgentHub Scaffold Status")
        table.add_column("Agent", style="cyan")
        table.add_column("ID", justify="right")
        table.add_column("Module")
        table.add_column("Prompt", justify="center")
        table.add_column("Remote", justify="center")
        table.add_column("Notes", style="magenta")

        client: ATTPClient | None = None
        connect_error: Exception | None = None

        try:
            client = self._build_client()
            await client.connect()
        except Exception as exc:  # pragma: no cover - connection issues are runtime dependent
            connect_error = exc

        for scaffold in scaffolds:
            dto, _ = self._build_local_agent(scaffold)
            prompt_exists = scaffold.prompt_path.exists()
            prompt_label = "yes" if prompt_exists else "no"
            remote_state = "N/A"
            remote_agent: IAgentResponse | None = None
            notes: list[str] = []

            if connect_error:
                remote_state = "[red]error[/red]"
                notes.append("AgentHub unreachable")
            elif client:
                try:
                    remote_agent, lookup_notes = await self._get_remote_agent(client, scaffold, dto)
                    notes.extend(lookup_notes)
                except Exception as exc:  # pragma: no cover
                    remote_state = "[red]error[/red]"
                    notes.append(str(exc))
                else:
                    if remote_agent is None:
                        remote_state = "[red]missing[/red]"
                        notes.append("Create with 'ascender run agents upgrade'")
                        if scaffold.agent_id is not None:
                            notes.append(f"No remote agent with id {scaffold.agent_id}")
                    else:
                        diff_fields = self._diff_agent(dto, remote_agent)
                        if diff_fields:
                            remote_state = "[yellow]update[/yellow]"
                            notes.append("Fields: " + ", ".join(diff_fields))
                        else:
                            remote_state = "[green]in sync[/green]"
                        if scaffold.agent_id and remote_agent.id != scaffold.agent_id:
                            notes.append(
                                f"ID mismatch (local {scaffold.agent_id}, remote {remote_agent.id})"
                            )
                        if scaffold.agent_id is None:
                            notes.append(f"Remote id {remote_agent.id}; consider setting AGENT_ID in scaffold")

            table.add_row(
                dto.name,
                str(remote_agent.id) if remote_agent else "-",
                dto.module_id,
                prompt_label,
                remote_state,
                "; ".join(notes) if notes else "",
            )

        if client:
            await client.close()

        if connect_error:
            self.console.print(f"[red]Failed to reach AgentHub:[/red] {connect_error}")

        self.console.print(table)

    @Handler("upgrade", description="Create missing AgentHub agents from scaffolds")
    async def upgrade_agents(
        self,
        dry_run: bool = Parameter(
            False,
            description="Only show actions without creating agents",
            names=["--dry-run"],
        ),
    ) -> None:
        scaffolds = self._discover_scaffolds()
        if not scaffolds:
            self.console.print("[yellow]No agent scaffolds found.[/yellow]")
            return

        client = self._build_client()
        try:
            await client.connect()
        except Exception as exc:
            self.console.print(f"[red]Failed to connect to AgentHub:[/red] {exc}")
            return

        created = 0
        updated = 0
        unchanged = 0
        try:
            for scaffold in scaffolds:
                dto, _ = self._build_local_agent(scaffold)
                remote_agent, lookup_notes = await self._get_remote_agent(client, scaffold, dto)

                for note in lookup_notes:
                    self.console.print(f"[yellow]{dto.name}: {note}[/yellow]")

                if remote_agent is None:
                    if dry_run:
                        self.console.print(f"[cyan]Would create agent {dto.name}[/cyan]")
                        created += 1
                        continue

                    response = await client.agents.create_agent(dto)
                    created += 1
                    self.console.print(
                        f"[green]Created agent {response.id}[/green] ({dto.name})"
                    )
                    if scaffold.agent_id and response.id != scaffold.agent_id:
                        self.console.print(
                            f"[yellow]Local AGENT_ID {scaffold.agent_id} differs from remote {response.id}; update scaffold.[/yellow]"
                        )
                    if scaffold.agent_id is None:
                        self.console.print(
                            f"[yellow]Set AGENT_ID={response.id} in scaffold for future sync.[/yellow]"
                        )
                    continue

                diff_fields = self._diff_agent(dto, remote_agent)
                if not diff_fields:
                    unchanged += 1
                    if dry_run:
                        self.console.print(f"[blue]{dto.name} is up to date.[/blue]")
                    continue

                fields_label = ", ".join(diff_fields)
                if dry_run:
                    self.console.print(
                        f"[cyan]Would update agent {remote_agent.id} ({dto.name}) fields: {fields_label}"
                    )
                    updated += 1
                    continue

                await client.agents.update_agent(remote_agent.id, dto)
                updated += 1
                self.console.print(
                    f"[green]Updated agent {remote_agent.id}[/green] ({dto.name}) fields: {fields_label}"
                )
                if scaffold.agent_id and remote_agent.id != scaffold.agent_id:
                    self.console.print(
                        f"[yellow]Local AGENT_ID {scaffold.agent_id} differs from remote {remote_agent.id}; update scaffold.[/yellow]"
                    )
                if scaffold.agent_id is None:
                    self.console.print(
                        f"[yellow]Remote id {remote_agent.id}; consider setting AGENT_ID in scaffold.[/yellow]"
                    )
        finally:
            await client.close()

        if dry_run:
            self.console.print(
                f"[blue]Dry run complete: create {created}, update {updated}, unchanged {unchanged}.[/blue]"
            )
        else:
            self.console.print(
                f"[green]Done. Created {created}, updated {updated}, unchanged {unchanged}.[/green]"
            )

    def _build_local_agent(self, scaffold: AgentScaffold) -> tuple[IAgentDTO, dict[str, Any]]:
        prompt_text = (
            scaffold.prompt_path.read_text(encoding="utf-8")
            if scaffold.prompt_path.exists()
            else None
        )
        manifest = scaffold.load_manifest(prompt_text)

        configuration = manifest.get("configuration")
        if hasattr(configuration, "model_dump"):
            configuration = configuration.model_dump(mode="json")  # type: ignore

        dto = IAgentDTO(
            name=manifest.get("name", scaffold.name),
            description=manifest.get("description", scaffold.description),
            module_id=manifest.get("module_id", scaffold.module_id),
            avatar_url=manifest.get("avatar_url"),
            configurations=configuration or {},
        )

        return dto, manifest

    async def _get_remote_agent(
        self,
        client: ATTPClient,
        scaffold: AgentScaffold,
        dto: IAgentDTO,
    ) -> tuple[IAgentResponse | None, list[str]]:
        try:
            remote = await client.agents.get_agent(agent_name=dto.name)
            return remote, []
        except (NotFoundError, CorrelatedRPCException):
            remote = None

        if scaffold.agent_id is not None:
            try:
                remote = await client.agents.get_agent(agent_id=scaffold.agent_id)
            except NotFoundError:
                return None, []

            notes: list[str] = []
            if remote.name != dto.name:
                notes.append(f"Will rename from '{remote.name}' to '{dto.name}'")
            return remote, notes

        return None, []

    @staticmethod
    def _diff_agent(dto: IAgentDTO, remote: IAgentResponse) -> list[str]:
        local = dto.model_dump(mode="json")
        remote_dump = remote.model_dump(mode="json")
        diffs: list[str] = []

        for key, value in local.items():
            remote_value = remote_dump.get(key)
            if key == "configurations":
                remote_value = remote_value or {}
                value = value or {}
            if remote_value != value:
                diffs.append(key)

        return diffs

    def _discover_scaffolds(self) -> list[AgentScaffold]:
        scaffolds: list[AgentScaffold] = []
        for path in sorted(self.scaffolds_dir.glob("*.py")):
            try:
                scaffolds.append(_load_scaffold(path))
            except Exception as exc:
                self.console.print(f"[red]Failed to load {path.name}:[/red] {exc}")
        return scaffolds

    def _discover_scaffold_modules(self) -> dict[str, ScaffoldModuleSpec]:
        specs: dict[str, ScaffoldModuleSpec] = {}
        for module in self.scaffold_engine.discover_scaffold_modules().values():
            specs[module.module_id] = ScaffoldModuleSpec(
                module_id=module.module_id,
                name=module.name,
                description=module.description,
                instance=module,
                path=Path("<package>"),
            )
        return specs

    def _build_client(self) -> ATTPClient:
        return ATTPClient(
            connection_url=self.settings.attp_url,
            agt_token=self.settings.agt_key,
            organization_id=self.settings.organization_id,
            limits=Limits(max_payload_size=600_000_000),
            logger=None,
        )
