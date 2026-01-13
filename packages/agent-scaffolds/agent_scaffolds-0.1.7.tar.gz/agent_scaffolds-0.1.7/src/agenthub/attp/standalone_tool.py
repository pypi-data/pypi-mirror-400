from __future__ import annotations

import dataclasses
import inspect
import traceback
from typing import Annotated, Any, Callable, get_args, get_origin, get_type_hints

from ascender.common import BaseDTO, BaseResponse
from attp_client import ATTPClient, AttpException, FixedBaseModel
from attp_client.interfaces.catalogs.tools.envelope import IEnvelope
from pydantic import BaseModel

from .context import CtxMarker
from .pipe import Pipe
from ..interfaces.types.tool_metadata import ToolMetadata


class StandaloneTool:
    def __init__(
        self,
        name: str,
        description: str | None,
        catalog: str,
        callback: Callable[..., Any],
    ) -> None:
        self.name = name
        self.description = description
        self.catalog = catalog
        self.callback = callback
        self.schema = self._extract_schema(callback)

    def __get__(self, instance: Any, owner: type | None = None) -> "StandaloneTool":
        if instance is None:
            return self
        bound = self.callback.__get__(instance, owner or type(instance))
        return StandaloneTool(
            name=self.name,
            description=self.description,
            catalog=self.catalog,
            callback=bound,
        )

    def _resolve_fixed_model(self, annotation: Any):
        if inspect.isclass(annotation) and issubclass(
            annotation, (FixedBaseModel, BaseModel, BaseDTO, BaseResponse)
        ):
            return annotation

        origin = get_origin(annotation)
        if inspect.isclass(origin) and issubclass(
            origin, (FixedBaseModel, BaseModel, BaseDTO, BaseResponse)
        ):
            return origin

        return None

    def _is_dataclass_type(self, annotation: Any) -> bool:
        return inspect.isclass(annotation) and dataclasses.is_dataclass(annotation)

    def _is_context_param(self, param: inspect.Parameter) -> bool:
        if isinstance(param.default, CtxMarker):
            return True

        annotation = param.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Annotated and any(isinstance(arg, CtxMarker) for arg in args[1:]):
            return True

        return False

    def _is_pipe_param(self, param: inspect.Parameter) -> bool:
        annotation = param.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Annotated and any(isinstance(arg, Pipe) for arg in args[1:]):
            return True

        return False

    def _get_pipe_param(self, param: inspect.Parameter) -> Pipe | None:
        annotation = param.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Annotated:
            for arg in args[1:]:
                if isinstance(arg, Pipe):
                    return arg
        return None

    def _extract_schema(self, callback: Any):
        type_hints = get_type_hints(callback)
        for param in inspect.signature(callback).parameters.values():
            if self._is_context_param(param) or self._is_pipe_param(param):
                continue

            annotation = self._resolve_annotation(param, type_hints)
            model = self._resolve_fixed_model(annotation)
            if model:
                return model.model_json_schema()
            if self._is_dataclass_type(annotation):
                return self._build_schema_from_dataclass(annotation)

        return self._build_schema_from_signature(callback)

    def _map_type_to_schema(self, annotation: Any) -> dict[str, Any]:
        origin = get_origin(annotation) or annotation
        args = get_args(annotation)

        if origin in (str, bytes):
            return {"type": "string"}
        if origin is bool:
            return {"type": "boolean"}
        if origin is int:
            return {"type": "integer"}
        if origin is float:
            return {"type": "number"}
        if origin is dict:
            return {"type": "object"}
        if origin in (list, tuple, set):
            items_schema = self._map_type_to_schema(args[0]) if args else {}
            return {"type": "array", "items": items_schema}
        return {}

    def _build_schema_from_signature(self, callback: Any) -> dict[str, Any] | None:
        sig = inspect.signature(callback)
        type_hints = get_type_hints(callback)
        properties: dict[str, Any] = {}
        required: list[str] = []

        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue

            if self._is_context_param(param) or self._is_pipe_param(param):
                continue

            annotation = self._resolve_annotation(param, type_hints)
            args = get_args(annotation)
            base_annotation = next((arg for arg in args if arg is not type(None)), annotation)

            schema = self._map_type_to_schema(base_annotation)
            properties[name] = schema

            default = param.default
            allows_none = type(None) in args
            if default is inspect._empty and not allows_none:
                required.append(name)

        if not properties:
            return None

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    def _build_schema_from_dataclass(self, model: type) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        for field in dataclasses.fields(model):
            schema = self._map_type_to_schema(field.type)
            properties[field.name] = schema
            if field.default is dataclasses.MISSING and field.default_factory is dataclasses.MISSING:
                required.append(field.name)
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }

    def _unwrap_annotation(self, annotation: Any) -> Any:
        origin = get_origin(annotation)
        if origin is Annotated:
            return get_args(annotation)[0]
        if args := get_args(annotation):
            return next((arg for arg in args if arg is not type(None)), annotation)
        return annotation

    def _resolve_annotation(
        self, param: inspect.Parameter, type_hints: dict[str, Any]
    ) -> Any:
        return type_hints.get(param.name, param.annotation)

    async def _build_kwargs_from_envelope(
        self, envelope: IEnvelope, callback: Any
    ) -> dict[str, Any]:
        sig = inspect.signature(callback)
        type_hints = get_type_hints(callback)
        data = envelope.data or {}
        kwargs: dict[str, Any] = {}
        model_params: dict[str, Any] = {}

        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue

            if self._is_context_param(param) or self._is_pipe_param(param):
                continue

            annotation = self._unwrap_annotation(
                self._resolve_annotation(param, type_hints)
            )
            model = self._resolve_fixed_model(annotation)
            if model is None and self._is_dataclass_type(annotation):
                model = annotation
            if model:
                model_params[name] = model

        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue

            if self._is_context_param(param):
                metadata: ToolMetadata = envelope.metadata or {}  # type: ignore
                kwargs[name] = metadata
                continue

            if self._is_pipe_param(param):
                pipe = self._get_pipe_param(param)
                if not pipe:
                    continue
                supply = pipe.supply(envelope)
                kwargs[name] = await supply if inspect.iscoroutine(supply) else supply
                continue

            if name in model_params:
                model = model_params[name]
                if self._is_dataclass_type(model):
                    kwargs[name] = model(**data)
                else:
                    kwargs[name] = model.model_validate(data)
                continue

            if name not in data and param.default is inspect._empty:
                raise ValueError(f"Missing required tool argument '{name}'")

            if name not in data:
                continue

            annotation = self._unwrap_annotation(
                self._resolve_annotation(param, type_hints)
            )
            model = self._resolve_fixed_model(annotation)
            value = data[name]

            if model:
                kwargs[name] = model.model_validate(value)
            elif self._is_dataclass_type(annotation) and isinstance(value, dict):
                kwargs[name] = annotation(**value)
            else:
                kwargs[name] = value

        return kwargs

    async def _invoke(self, envelope: IEnvelope):
        try:
            kwargs = await self._build_kwargs_from_envelope(envelope, self.callback)
            if inspect.iscoroutinefunction(self.callback):
                return await self.callback(**kwargs)
            return self.callback(**kwargs)
        except Exception as exc:
            traceback.print_exc()
            raise AttpException(
                detail={"message": f"Error invoking ATTP tool '{self.name}': {exc}"}
            ) from exc

    async def attach(self, client: ATTPClient) -> None:
        catalog = await client.catalog(self.catalog)
        catalog.attach_tool(
            self._invoke,
            self.name,
            description=self.description or self.callback.__doc__,
            schema=self.schema,
            schema_id=self.name + "_schema",
            schema_ver="2.0",
        )

    async def detach(self, client) -> None:
        catalog = await client.catalog(self.catalog)
        await catalog.detach_tool(self.name)


def tool(
    name: str,
    description: str | None = None,
    *,
    catalog: str = "default",
) -> Callable[[Callable[..., Any]], StandaloneTool]:
    def decorator(func: Callable[..., Any]) -> StandaloneTool:
        return StandaloneTool(name=name, description=description, catalog=catalog, callback=func)

    return decorator
