from __future__ import annotations

import importlib
import importlib.resources as resources
import importlib.util
import inspect
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agenthub.interfaces.scaffold_module import ScaffoldModule


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "agent"


def _python_repr(value: str | None) -> str:
    return "None" if value is None else repr(value)


@dataclass(slots=True)
class ScaffoldGenerationSpec:
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
    scaffolds_dir: Path | None = None


class ScaffoldEngine:
    def __init__(self, scaffolds_dir: Path | None = None) -> None:
        self.scaffolds_dir = scaffolds_dir or (Path.cwd() / "scaffolds")

    def discover_scaffold_modules(self) -> dict[str, ScaffoldModule]:
        modules: dict[str, ScaffoldModule] = {}

        def _load_module(module_name: str) -> None:
            try:
                mod = importlib.import_module(module_name)
            except Exception:
                return
            for obj in mod.__dict__.values():
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, ScaffoldModule)
                    and obj is not ScaffoldModule
                ):
                    instance = obj()
                    if instance.module_id and instance.module_id not in modules:
                        modules[instance.module_id] = instance

        # Try packaged resources first
        try:
            pkg_files = resources.files("agenthub.scaffolds")
            for entry in pkg_files.iterdir():
                if entry.name.endswith(".py") and entry.name != "__init__.py":
                    _load_module(f"agenthub.scaffolds.{entry.name[:-3]}")
        except Exception:
            pass

        # Fallback to local filesystem if nothing found
        if not modules:
            local_dir = Path(__file__).resolve().parents[2] / "scaffolds"
            for path in local_dir.glob("*.py"):
                if path.name == "__init__.py":
                    continue
                module_name = f"agenthub.scaffolds.{path.stem}"
                spec = importlib.util.spec_from_file_location(module_name, path)
                if not spec or not spec.loader:
                    continue
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                try:
                    spec.loader.exec_module(mod)
                except Exception:
                    continue
                for obj in mod.__dict__.values():
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, ScaffoldModule)
                        and obj is not ScaffoldModule
                    ):
                        instance = obj()
                        if instance.module_id and instance.module_id not in modules:
                            modules[instance.module_id] = instance

        return modules

    def generate_scaffold(self, spec: ScaffoldGenerationSpec) -> dict[str, Any]:
        modules = self.discover_scaffold_modules()
        if not modules:
            raise RuntimeError("No scaffold modules available.")

        module = modules.get(spec.module_id)
        if not module:
            raise RuntimeError(
                f"Unknown module_id '{spec.module_id}'. Available: {list(modules.keys())}"
            )

        slug = _slugify(spec.name)
        scaffolds_dir = self.scaffolds_dir
        scaffold_path = scaffolds_dir / f"{slug}.py"
        prompt_path = scaffold_path.with_suffix(".prompt")

        if scaffold_path.exists() and not spec.overwrite:
            raise FileExistsError(
                f"Scaffold {scaffold_path} exists. Set overwrite=True to replace."
            )

        description = spec.description or f"{spec.name} agent description"
        instruction_template = spec.instruction_template or (
            "You are an AgentHub agent. Fall back to this instruction when no prompt is provided."
        )

        context = {
            "agent_name": spec.name,
            "agent_name_repr": repr(spec.name),
            "agent_id": spec.agent_id,
            "description_repr": repr(description),
            "module_id": spec.module_id,
            "module_id_repr": repr(spec.module_id),
            "llm_load_string_repr": repr(spec.llm_load_string),
            "prompt_filename_repr": repr(prompt_path.name),
            "instruction_template_repr": repr(instruction_template),
            "avatar_url_repr": _python_repr(spec.avatar_url),
            "attp_catalog_repr": _python_repr(spec.attp_catalog),
            "enable_attp": True,
            "enable_tables_reading": False,
        }

        prompt_default = module.make_prompt_template(context)
        prompt_content = spec.prompt_text or prompt_default
        scaffold_content = module.generate_manifest(context)

        scaffolds_dir.mkdir(parents=True, exist_ok=True)
        scaffold_path.write_text(scaffold_content.rstrip() + "\n", encoding="utf-8")
        prompt_path.write_text(prompt_content.rstrip() + "\n", encoding="utf-8")

        return {
            "slug": slug,
            "module_id": module.module_id,
            "scaffold_path": str(scaffold_path),
            "prompt_path": str(prompt_path),
        }
