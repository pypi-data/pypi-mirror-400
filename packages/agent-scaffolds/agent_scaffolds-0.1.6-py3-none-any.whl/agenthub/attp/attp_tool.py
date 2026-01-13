import inspect
import traceback
from typing import Annotated, Any, get_args, get_origin

from ascender.common import BaseDTO, BaseResponse
from ascender.core import Application, ControllerDecoratorHook, inject
from attp_client import ATTPClient, AttpException, FixedBaseModel
from attp_client.interfaces.catalogs.tools.envelope import IEnvelope
from pydantic import BaseModel

from .context import CtxMarker
from .pipe import Pipe
from ..interfaces.types.tool_metadata import ToolMetadata


class AttpTool(ControllerDecoratorHook):
    """
    A controller decorator hook for ATTP tool integration.
    
    It registers ATTP Tool in scope of selected category provided in the decorator parameters.
    It executes the callback function as soon as AgentHub Agent calls the tool correlated with this decorator.
    """
    attp_client: ATTPClient = inject(ATTPClient)
    application: Application = inject(Application)
    
    def __init__(
        self, 
        name: str,
        description: str | None = None,
        catalog: str = "default"
    ) -> None:
        super().__init__()
        
        self.name = name
        self.description = description
        self.catalog = catalog

    def __resolve_fixed_model(self, annotation: Any):
        """Return FixedBaseModel subclass if present in annotation."""
        if inspect.isclass(annotation) and issubclass(annotation, (FixedBaseModel, BaseModel, BaseDTO, BaseResponse)):
            return annotation

        origin = get_origin(annotation)
        if inspect.isclass(origin) and issubclass(origin, (FixedBaseModel, BaseModel, BaseDTO, BaseResponse)):
            return origin

        return None

    def __is_context_param(self, param: inspect.Parameter) -> bool:
        if isinstance(param.default, CtxMarker):
            return True

        annotation = param.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Annotated and any(isinstance(arg, CtxMarker) for arg in args[1:]):
            return True

        return False

    def __is_pipe_param(self, param: inspect.Parameter) -> bool:
        annotation = param.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Annotated and any(isinstance(arg, Pipe) for arg in args[1:]):
            return True

        return False
    
    def get_pipe_param(self, param: inspect.Parameter) -> Pipe | None:
        annotation = param.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Annotated:
            for arg in args[1:]:
                if isinstance(arg, Pipe):
                    return arg
        return None

    def __extract_schema(self, callback: Any):
        """Extract schema from the callback's annotations if it uses FixedBaseModel."""
        for param in inspect.signature(callback).parameters.values():
            if self.__is_context_param(param):
                continue
            
            if self.__is_pipe_param(param):
                continue

            annotation = param.annotation
            model = self.__resolve_fixed_model(annotation)
            if model:
                return model.model_json_schema()

        return self.__build_schema_from_signature(callback)

    def __map_type_to_schema(self, annotation: Any) -> dict[str, Any]:
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
            items_schema = self.__map_type_to_schema(args[0]) if args else {}
            return {"type": "array", "items": items_schema}
        # Fallback to permissive schema for unknown types
        return {}

    def __build_schema_from_signature(self, callback: Any) -> dict[str, Any] | None:
        sig = inspect.signature(callback)
        properties: dict[str, Any] = {}
        required: list[str] = []

        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue

            if self.__is_context_param(param):
                continue

            annotation = param.annotation
            args = get_args(annotation)
            base_annotation = next((arg for arg in args if arg is not type(None)), annotation)

            schema = self.__map_type_to_schema(base_annotation)
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
            "required": required
        }

    def __unwrap_annotation(self, annotation: Any) -> Any:
        origin = get_origin(annotation)
        if origin is Annotated:
            return get_args(annotation)[0]
        if args := get_args(annotation):
            return next((arg for arg in args if arg is not type(None)), annotation)
        return annotation

    async def __build_kwargs_from_envelope(self, envelope: IEnvelope, callback: Any) -> dict[str, Any]:
        sig = inspect.signature(callback)
        data = envelope.data or {}
        kwargs: dict[str, Any] = {}
        model_params: dict[str, Any] = {}

        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue

            if self.__is_context_param(param) or self.__is_pipe_param(param):
                continue

            annotation = self.__unwrap_annotation(param.annotation)
            model = self.__resolve_fixed_model(annotation)
            if model:
                model_params[name] = model

        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue

            if self.__is_context_param(param):
                metadata: ToolMetadata = envelope.metadata or {} # type: ignore
                kwargs[name] = metadata
                continue
            
            if self.__is_pipe_param(param):
                pipe = self.get_pipe_param(param)
                if not pipe:
                    continue
                supply = pipe.supply(envelope)
                
                if inspect.iscoroutine(supply):
                    kwargs[name] = await supply
                    continue
                
                kwargs[name] = supply
                continue

            if name in model_params:
                kwargs[name] = model_params[name].model_validate(data)
                continue

            if name not in data and param.default is inspect._empty:
                raise ValueError(f"Missing required tool argument '{name}'")

            if name not in data:
                continue  # default will be used by Python

            annotation = self.__unwrap_annotation(param.annotation)
            model = self.__resolve_fixed_model(annotation)
            value = data[name]
                
            kwargs[name] = model.model_validate(value) if model else value

        return kwargs

    def on_load(self, callback):
        schema = self.__extract_schema(callback)

        async def _invoke(envelope: IEnvelope):
            try:
                kwargs = await self.__build_kwargs_from_envelope(envelope, callback)
                return await callback(**kwargs)
            except Exception as e:
                traceback.print_exc()
                raise AttpException(detail={"message": f"Error invoking ATTP tool '{self.name}': {e}"}) from e

        async def _attach():
            catalog = await self.attp_client.catalog(self.catalog)
            catalog.attach_tool(
                _invoke,
                self.name,
                description=self.description or callback.__doc__,
                schema=schema,
                schema_id=self.name + "_schema",
                schema_ver="2.0"
            )
        
        async def _detach():
            print(f"Detatching tool from ATTP... {self.name}")
            catalog = await self.attp_client.catalog(self.catalog)
            catalog.detach_tool(self.name)

        self.application.app.add_event_handler("startup", _attach)
        self.application.app.add_event_handler("shutdown", _detach)
