from abc import ABC, abstractmethod
from typing import Any

from attp_client import IEnvelope


class Pipe(ABC):
    """
    > One wise man said: No message walks alone; even the most anonymous words drag their shadows of paper, language, and form are tiny traces that reveal how they came to be.
    
    So far pipes are designed to avoid repitative code by supplying commonly used context data from the envelope metadata.
    Design pipe once - use everywhere.
    
    Envelope contains crucial context information of:
    - Where tool is being called (which chat)
    - What agent is calling the tool (ID of the agent in agenthub)
    - In what catalog the tool is registered (catalog name)
    
    The most common use is `chat_id` from metadata to fetch user and chat information from the database.
    Every backend has its unique design even if they copy. But when they use AgentHub, they share the one common thing - chat_id.
    So pipes help people to design and automate the extraction of such common context data and conversion to whatever they need for their system.
    """
    ...
    
    @abstractmethod
    def supply(self, envelope: IEnvelope) -> Any:
        ...
    
    async def asupply(self, envelope: IEnvelope) -> Any:
        raise NotImplementedError("Asynchronous supply is not implemented for this pipe.")