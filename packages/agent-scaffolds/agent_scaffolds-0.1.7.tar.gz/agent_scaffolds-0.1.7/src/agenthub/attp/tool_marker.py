from typing import Any, Callable, Mapping

from pydantic import validate_call

from attp_client import AttpCatalog, FixedBaseModel, IEnvelope


class ToolKind:
    def __init__(
        self, 
        metadata: dict[str, Any],
        callback: Callable[..., Any]
    ) -> None:
        self.metadata = metadata
        self.callback = validate_call(config={"arbitrary_types_allowed": True})(callback)

    async def execute_cb(self, envelope: IEnvelope) -> Any:
        return await self.callback(data=envelope.data, metadata=envelope.metadata)
    
    async def attach(self, catalog: AttpCatalog):
        catalog.attach_tool(
            self.execute_cb,
            self.metadata["name"],
            description=self.metadata.get("description"),
            schema=self.metadata.get("schema"),
            schema_id=self.metadata.get("schema_id"),
            return_direct=self.metadata.get("return_direct", False),
            schema_ver=self.metadata.get("schema_ver", "1.0"),
            timeout_ms=self.metadata.get("timeout_ms", 20000),
            idempotent=self.metadata.get("idempotent", False)
        )
    
def tool(
    name: str, 
    description: str | None = None,
    schema: type[FixedBaseModel] | dict | None = None,
    schema_id: str | None = None,
    *,
    return_direct: bool = False,
    schema_ver: str = "2.0",
    timeout_ms: float = 20000,
    idempotent: bool = False
):
    def decorator(func):
        metadata = {
            "name": name,
            "description": description or func.__doc__ or "",
            "schema": schema.model_json_schema() if isinstance(schema, type) and issubclass(schema, FixedBaseModel) else schema,
            "schema_id": schema_id,
            "return_direct": return_direct,
            "schema_ver": schema_ver,
            "timeout_ms": timeout_ms,
            "idempotent": idempotent
        }
        return ToolKind(metadata, func)
    return decorator