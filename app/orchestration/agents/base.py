from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, TypeVar

from app.orchestration.services import LLMService

StateT = TypeVar("StateT", bound=Mapping[str, Any])
OutputT = TypeVar("OutputT", bound=Mapping[str, Any])


class BaseAgent(Generic[StateT, OutputT], ABC):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    @abstractmethod
    async def process(self, state: StateT) -> OutputT:
        pass
