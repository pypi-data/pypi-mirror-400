from abc import ABC, abstractmethod
from typing import Any, Callable


class ScaffoldModule(ABC):
    module_id: str = ""
    name: str = ""
    description: str = ""

    @abstractmethod
    def generate_manifest(self, context: dict[str, Any]) -> str:
        """
        Generates a code for scaffold manifest, defining basic values of agent.

        Returns:
            str: A python boilerplate/template code for scaffold manifest.
        """
        raise NotImplementedError("Subclasses must implement generate_manifest method")

    @abstractmethod
    def make_prompt_template(self, context: dict[str, Any]) -> str:
        """
        Either generates a prompt template (if it follows some standard structure or pattern)
        or return a string with default or basic prompt for the module.
        """
        raise NotImplementedError("Subclasses must implement make_prompt_template method")

    @abstractmethod
    def load_scaffold(
        self, loader: Callable[[Any | None], dict[str, Any]], agent_id: int | None = None
    ) -> Any:
        """Loads a scaffold using the provided loader callable and optional agent ID.

        Args:
            loader (Callable[[Any | None], dict[str, Any]]): A callable that takes an optional argument and returns a dictionary of scaffold data.
            agent_id (int | None, optional): An optional agent ID to be used during loading. Defaults to None.

        Returns:
            Any: The loaded scaffold object.
        """
        raise NotImplementedError("Subclasses must implement load_scaffold method")
