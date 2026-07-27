from langgraph.graph import START, StateGraph

from app.orchestration.agents.router_agent import RouterAgent
from app.orchestration.graphs.states import GraphState, RouterInput, RouterOutput
from app.orchestration.services import LLMService
from app.repositories import SessionMessageRepository

AGENT_ROLE = "agent"
USER_ROLE = "user"


class MainGraph:
    def __init__(
        self,
        llm_service: LLMService,
        message_repo: SessionMessageRepository | None = None,
    ):
        self.llm_service = llm_service
        self.router_agent = RouterAgent(llm_service)
        self.message_repo = message_repo
        self.graph = self._build_graph().compile()

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

        # Save the router's decision as an agent message in the DB
        await self._save_node_output(
            state=state,
            node_name="router",
            content=f"Routing category: {router_output['routing_category']}",
        )

        return router_output

    async def _save_node_output(
        self, state: GraphState, node_name: str, content: str
    ) -> None:
        """Persist a node's output as an agent message in the database."""
        if self.message_repo is None:
            return

        session_id = state.get("session_id", "")
        if not session_id:
            return

        user_id = state.get("user_id", "default")
        sequence_number = await self.message_repo.get_next_sequence_number(session_id)

        await self.message_repo.save_message(
            user_id=user_id,
            session_id=session_id,
            role=AGENT_ROLE,
            sequence_number=sequence_number,
            content=content,
            model=None,
        )
