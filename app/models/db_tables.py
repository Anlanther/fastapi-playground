from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)


def get_users_table(metadata: MetaData) -> Table:
    return Table(
        "users",
        metadata,
        Column("id", String(36), primary_key=True, index=True),
        Column("username", String(50), unique=True, nullable=False),
    )


def get_sessions_table(metadata: MetaData) -> Table:
    return Table(
        "sessions",
        metadata,
        Column("id", String(36), primary_key=True, index=True),
        Column("summary", String(100), nullable=False),
    )


def get_session_messages_table(metadata: MetaData) -> Table:
    return Table(
        "session_messages",
        metadata,
        Column("id", String(36), primary_key=True, index=True),
        Column(
            "user_id", String(36), ForeignKey("users.id"), nullable=False, index=True
        ),
        Column(
            "session_id",
            String(36),
            ForeignKey("sessions.id"),
            nullable=False,
            index=True,
        ),
        Column("role", String(20), nullable=False),
        Column("sequence_number", Integer, nullable=False),
        Column("content", Text, nullable=True),
        Column("model", Text, nullable=True),
        Column("created_at", DateTime, nullable=False),
    )
