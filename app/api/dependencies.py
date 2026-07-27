from app.orchestration.services import LLMService


class DependencyContainer:
    def __init__(self):
        self._llm_service: LLMService | None = None

    def get_llm_service(self) -> LLMService:
        if self._llm_service is None:
            self._llm_service = LLMService()
        return self._llm_service


container = DependencyContainer()


def get_llm_service() -> LLMService:
    return container.get_llm_service()
