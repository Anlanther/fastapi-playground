from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Discriminator
from sqlalchemy import Boolean, Column, Integer, MetaData, String, Table, Text


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


def get_users_table(metadata: MetaData) -> Table:
    """Define the users table."""
    return Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('username', String(50), unique=True, nullable=False),
        Column('email', String(255), unique=True, nullable=False),
    )


def get_products_table(metadata: MetaData) -> Table:
    """Define the products table (example for multiple tables)."""
    return Table(
        'products',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String(100), nullable=False),
        Column('price', Integer, nullable=False),
    )


def get_session_messages_table(metadata: MetaData) -> Table:
    """Define a generic session messages table to store conversation events.

    Fields are intentionally generic to support multiple workflows:
    - `session_id`: logical grouping for a conversation or workflow
    - `role`: who produced the message (user|agent|system)
    - `span_id`: optional checkpoint identifier for approval points
    - `approved`: optional boolean set when a human approves a span
    - `payload`: JSON/text blob of the message content or metadata
    - `tokens_estimate`: optional integer tokens estimate for cost tracking
    - `created_at`: timestamp for ordering
    """
    from datetime import datetime

    from sqlalchemy import DateTime

    return Table(
        'session_messages',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('session_id', String(255), nullable=False, index=True),
        Column('role', String(50), nullable=False, default='agent'),
        Column('span_id', String(255), nullable=True, index=True),
        Column('approved', Boolean, nullable=True),
        Column('payload', Text, nullable=True),
        Column('tokens_estimate', Integer, nullable=True),
        Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
    )
