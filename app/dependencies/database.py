from fastapi import Request

from app.core import Database
from app.core.config import settings
from app.models import get_session_messages_table, get_sessions_table, get_users_table


def initialize_database() -> Database:
    db = Database(settings.database_url)
    db.register_table("users", get_users_table(db.metadata))
    db.register_table("users", get_sessions_table(db.metadata))
    db.register_table("users", get_session_messages_table(db.metadata))
    return db


async def get_db(request: Request) -> Database:
    return request.app.state.db
