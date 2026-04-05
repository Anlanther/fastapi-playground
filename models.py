from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Discriminator


class Type(Enum):
    THINK = "think"
    SUGGESTION = "suggestion"
    LOG = "log"
    TEXT = "text"
    CHUNKS = "chunks"

class Chunk(BaseModel):
    document_id: str
    chunk_id: str
    title: str
    text: str      

class TextResponse(BaseModel):
    type: Literal[Type.TEXT] = Type.TEXT
    text: str
    
class ThinkResponse(BaseModel):
    type: Literal[Type.THINK] = Type.THINK
    text: str    
    
class LogResponse(BaseModel):
    type: Literal[Type.LOG] = Type.LOG
    span_id: str
    
class ChunksResponse(BaseModel):
    type: Literal[Type.CHUNKS] = Type.CHUNKS
    chunks: list[Chunk]

def get_discriminator(v: Union[TextResponse, ThinkResponse, LogResponse, ChunksResponse]) -> str:
    return v.type.value

AgentResponse = Annotated[
    Union[TextResponse, ThinkResponse, LogResponse, ChunksResponse],
    Discriminator(get_discriminator),
]
    