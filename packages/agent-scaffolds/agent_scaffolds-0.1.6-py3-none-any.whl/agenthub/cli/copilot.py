"""AgentHub copilot CLI."""

from __future__ import annotations

from pathlib import Path

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
        self.scaffolds_dir = SRC_DIR / "scaffolds"

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
            f"[green]Scaffold created:[/green] {scaffold_path.relative_to(PROJECT_ROOT)}"
        )
        self.console.print(
            f"[green]Prompt created:[/green] {prompt_path.relative_to(PROJECT_ROOT)}"
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
        scaffold_path = self.scaffolds_dir / "agent_creation_copilot.py"
        if not scaffold_path.exists():
            self.console.print("[red]Copilot scaffold not found.[/red]")
            self.console.print("[yellow]Generate it with 'ascender run copilot scaffold'.[/yellow]")
            return

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

        try:
            await client.connect()
        except Exception as exc:
            self.console.print(f"[red]Failed to connect to AgentHub:[/red] {exc}")
            return

        try:
            await run_copilot_tui(
                client=client,
                agent_name=agent_name,
                chat_name=chat_name,
            )
        finally:
            await client.close()
