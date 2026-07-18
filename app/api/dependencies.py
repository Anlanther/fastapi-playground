from typing import Optional

from app.orchestration.graphs import MainGraph
from app.orchestration.services import LLMService


class DependencyContainer:
    def __init__(self):
        self._llm_service: Optional[LLMService] = None
        # self._session_service: Optional[SessionService] = None
        # self._message_repo: Optional[MessageRepository] = None
        self._graph: Optional[MainGraph] = None

    def get_llm_service(self) -> LLMService:
        if self._llm_service is None:
            self._llm_service = LLMService()
        return self._llm_service

    def get_graph(self) -> MainGraph:
        if self._graph is None:
            self._graph = MainGraph(self.get_llm_service())
        return self._graph


container = DependencyContainer()


def get_llm_service() -> LLMService:
    return container.get_llm_service()


def get_graph() -> MainGraph:
    return container.get_graph()
