import json

from app.core import Database
from app.orchestration.graphs import GraphState, MainGraph
from app.orchestration.services import LLMService
from app.repositories import SessionMessageRepository


class ChatGraphService:
    def __init__(self, db: Database, llm_service: LLMService):
        self.message_repo = SessionMessageRepository(db)
        self.graph = MainGraph(llm_service, message_repo=self.message_repo)

    async def build_initial_state(
        self,
        message: str,
        session_id: str,
        user_id: str,
    ) -> GraphState:
        history = await self.message_repo.get_conversation_history(session_id)

        seq = await self.message_repo.get_next_sequence_number(session_id)
        await self.message_repo.save_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            sequence_number=seq,
            content=message,
        )

        # Add the just-saved message so the graph sees it
        history.append({"role": "user", "content": message})

        return GraphState(
            user_query=message,
            session_id=session_id,
            user_id=user_id,
            conversation_history=history,
            next_node="router_node",
            routing_category="",
        )

    async def stream_graph(self, state: GraphState):
        """Yield JSON-line strings for each node update as the graph runs."""
        async for event in self.graph.graph.astream(state, stream_mode="updates"):
            for node_name, node_output in event.items():
                yield json.dumps({"node": node_name, "output": node_output}) + "\n"
