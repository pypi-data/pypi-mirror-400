from typing import Any


class CtxMarker:
    """Marker for injecting tool invocation context (metadata)."""


def Ctx() -> Any:
    return CtxMarker()
