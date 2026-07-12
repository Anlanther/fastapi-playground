from collections.abc import AsyncIterator

from app.core import Database
from app.core.config import settings
from app.models import get_users_table, get_session_messages_table


def get_database() -> Database:
    db = Database(settings.database_url)
    db.register_table("users", get_users_table(db.metadata))
    db.register_table("session_messages", get_session_messages_table(db.metadata))
    return db


async def get_db() -> AsyncIterator[Database]:
    db = get_database()
    try:
        await db.init_db()
        yield db
    finally:
        await db.engine.dispose()
