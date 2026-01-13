from typing import Any, Callable
from ascender.core import ControllerDecoratorHook, inject

from fastapi_mcp import FastApiMCP
from mcp.types import ToolAnnotations, Icon


class MCPTool(ControllerDecoratorHook):
    server: FastApiMCP | None = inject(FastApiMCP, None)
    
    def __init__(
        self,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        annotations: ToolAnnotations | None = None,
        icons: list[Icon] | None = None,
        meta: dict[str, Any] | None = None,
        structured_output: bool | None = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.title = title
        self.description = description
        self.annotations = annotations
        self.icons = icons
        self.meta = meta
        self.structured_output = structured_output
    
    def on_load(self, callable: Callable[..., Any]):
        if not self.server:
            raise RuntimeError("MCPTool hook requires FastApiMCP server instance.")
        pass