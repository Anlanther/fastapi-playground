from langgraph.graph import START, StateGraph

from app.orchestration.agents import RouterAgent
from app.orchestration.graphs import GraphState, RouterInput, RouterOutput
from app.orchestration.services import LLMService


class MainGraph:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.router_agent = RouterAgent(llm_service)
        # self.graph = self

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(GraphState)

        workflow.add_node("router", self.router_node)

        workflow.add_edge(START, "router")

        return workflow

    async def router_node(self, state: GraphState) -> RouterOutput:
        router_input: RouterInput = {
            "user_query": state.get("user_query", ""),
            "conversation_history": state.get("conversation_history", []),
        }

        router_output = await self.router_agent.process(router_input)

        return {**router_output}
