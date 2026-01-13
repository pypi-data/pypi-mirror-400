"""AgentHub copilot CLI."""

from __future__ import annotations

from pathlib import Path
import inspect

from ascender.core.cli_engine import Command, GenericCLI, Handler, Parameter
from attp_client.client import ATTPClient
from attp_core.rs_api import Limits
from rich.console import Console
from rich.prompt import Confirm

from agenthub.configs.main import load_agenthub_config
from agenthub.copilot.sdk import AgentCreationCopilotSDK
from agenthub.copilot.ui import run_copilot_tui


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT / "src"


@Command(name="copilot", description="AgentHub copilot utilities")
class CopilotCLI(GenericCLI):
    def __init__(self) -> None:
        super().__init__()
        self.console = Console()
        # In library mode, use CWD/scaffolds so packaged installs work without repo layout
        self.scaffolds_dir = Path.cwd() / "scaffolds"

    @Handler("scaffold", description="Generate the agent-creation-copilot scaffold")
    async def generate_scaffold(
        self,
        overwrite: bool = Parameter(
            False,
            description="Overwrite existing scaffold files",
            names=["-f", "--force"],
        ),
    ) -> None:
        sdk = AgentCreationCopilotSDK()
        scaffold_path, prompt_path = sdk.scaffold_paths()

        if (scaffold_path.exists() or prompt_path.exists()) and not overwrite:
            if not Confirm.ask("Scaffold exists. Overwrite?"):
                self.console.print("[yellow]Aborted - existing files left untouched.[/yellow]")
                return

        if overwrite and (scaffold_path.exists() or prompt_path.exists()):
            if not Confirm.ask("Overwrite existing scaffold files?"):
                self.console.print("[yellow]Aborted - existing files left untouched.[/yellow]")
                return

        sdk.write_scaffold(overwrite=True)
        self.console.print(
            f"[green]Scaffold created:[/green] {scaffold_path}"  # already under CWD/scaffolds
        )
        self.console.print(
            f"[green]Prompt created:[/green] {prompt_path}"
        )

    @Handler("run", description="Run the copilot via ATTP")
    async def run_copilot(
        self,
        subject: str | None = Parameter(
            None,
            description="Optional subject. If omitted, the most recent chat is reused.",
            names=["--subject"],
        ),
    ) -> None:
        config = load_agenthub_config()
        client = ATTPClient(
            connection_url=config.attp_url,
            agt_token=config.agt_key,
            organization_id=config.organization_id,
            limits=Limits(max_payload_size=600_000_000),
            logger=None,
        )

        sdk = AgentCreationCopilotSDK()
        agent_name = sdk.spec.agent_name
        chat_name = f"Agent Copilot Session {subject}" if subject else None
        scaffold_path = self.scaffolds_dir / "agent_creation_copilot.py"

        try:
            await client.connect()
        except Exception as exc:
            self.console.print(f"[red]Failed to connect to AgentHub:[/red] {exc}")
            return

        try:
            # Resolve copilot agent by name; require it to exist remotely.
            candidates: list = []
            get_agents = getattr(client.agents, "get_agents", None)
            if callable(get_agents):
                try:
                    if inspect.iscoroutinefunction(get_agents):
                        agents_response = await get_agents(search=agent_name)
                    else:
                        agents_response = get_agents(search=agent_name)
                    items = getattr(agents_response, "items", []) or []
                    candidates = [a for a in items if getattr(a, "name", None) == agent_name]
                except Exception:
                    candidates = []

            if not candidates:
                self.console.print(
                    "[red]Copilot agent not found in AgentHub.[/red]"
                )
                self.console.print(
                    "[yellow]Create and sync the copilot scaffold (ascender run copilot scaffold) and deploy it so the agent named '%s' exists.[/yellow]"
                    % agent_name
                )
                if not scaffold_path.exists():
                    self.console.print(
                        "[yellow]Tip: run this in your project root so files land under ./scaffolds/.[/yellow]"
                    )
                return

            await run_copilot_tui(
                client=client,
                agent_name=agent_name,
                chat_name=chat_name,
            )
        finally:
            await client.close()
