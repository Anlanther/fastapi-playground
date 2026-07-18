from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic import BaseModel

from app.api.dependencies import get_graph
from app.orchestration.graphs import GraphState, MainGraph


class ChatRequest(BaseModel):
    message: str
    session_id: str

router = APIRouter(prefix="/chat-graph", tags=["Chat Graph"])

@router.post("/stream")
async def chat_stream(request: ChatRequest, graph: MainGraph = Depends(get_graph)):
    try:
        state: GraphState = {
            "user_query": request.message,
            "conversation_history": [],
            "next_node": "router_node",
            "routing_category": "",
            "session_id": ""
        }
    except:
    #     #test
    # finally:
    #     yield "data: [DONE]\n\n"
