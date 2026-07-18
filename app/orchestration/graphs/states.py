from typing import Dict, List

from typing_extensions import TypedDict


class InputState(TypedDict):
    user_query: str
    session_id: str
    conversation_history: List[Dict[str, str]]


class RouterInput(TypedDict):
    user_query: str
    conversation_history: List[Dict[str, str]]


class RouterOutput(TypedDict):
    routing_category: str
    next_node: str
    # routing_token_count: int

    # research_result: str
    # research_intermediate_steps: List[Dict[str, Any]]


class GraphState(InputState, RouterOutput):
    pass
