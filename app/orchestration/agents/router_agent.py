import json
from typing import cast

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic.v1.main import BaseModel

from app.orchestration.agents import BaseAgent
from app.orchestration.graphs import RouterInput, RouterOutput

AGENT_SYSTEM_MESSAGE = """You are a router agent tasked to categorise user messages. Depending on the category, a specialised agent will take over the task.

Categories:
    - "research"
    - "general"
    - "action"
"""


class SuggestedCategory(BaseModel):
    category: str


class RouterAgent(BaseAgent[RouterInput, RouterOutput]):
    async def process(self, state: RouterInput) -> RouterOutput:
        user_query = state.get("user_query")
        conversation_history = state.get("conversation_history")

        llm = self.llm_service.get_llm()
        structured_llm = llm.with_structured_output(SuggestedCategory)

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=AGENT_SYSTEM_MESSAGE),
                *conversation_history[-5:],
                HumanMessage(content=user_query),
            ]
        )

        response = cast(
            SuggestedCategory, await structured_llm.ainvoke(prompt.format_messages())
        )
        category = response.category

        output: RouterOutput = {
            "routing_category": category,
            "next_node": category if category != "general" else "chat",
        }

        return output
