from typing import Any
from ascender.core import Application, Provider
from fastapi_mcp import FastApiMCP


class LifeCycleHook:
    def __init__(self, application: Application, **data) -> None:
        self.instance = FastApiMCP(**data)
        self.application = application
                
    def __call__(self) -> Any:
        self.instance.mount_http()
        return self.instance


def provideMCP(
    name: str | None = None,
    description: str | None = None,
    **additional_kwargs: Any,
) -> Provider:
    return {
        "provide": FastApiMCP,
        "use_factory": lambda a: LifeCycleHook(a, name=name, description=description, **additional_kwargs),
        "deps": [Application],
    }