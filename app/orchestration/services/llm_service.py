from langchain_openai import ChatOpenAI

from app.core.config import settings

DEFAULT_MODEL = "qwen3.5-9b"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_STREAMING_MODE = False


class LMStudioLLM(ChatOpenAI):
    def __init__(self, model_name: str, temperature: float, streaming: bool, **kwargs):
        super().__init__(
            base_url=settings.lm_endpoint,
            api_key=None,
            model=model_name,
            temperature=temperature,
            streaming=streaming,
            max_retries=settings.lm_max_retries,
            **kwargs,
        )


class LLMService:
    # def __init__(self)
    def get_llm(
        self,
        model_name: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        streaming: bool = DEFAULT_STREAMING_MODE,
    ):
        llm = LMStudioLLM(
            model_name=model_name, temperature=temperature, streaming=streaming
        )
        return llm
