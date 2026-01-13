from uuid import UUID

from typing_extensions import TypedDict


class ToolMetadata(TypedDict, total=False):
    chat_id: UUID | str
    agent_id: int
    organization_id: int
