from collections.abc import AsyncIterator

from app.core import Database
from app.core.config import settings
from app.models import get_users_table


def initialize_database() -> Database:
    db = Database(settings.database_url)
    db.register_table("users", get_users_table(db.metadata))
    return db


async def get_db() -> AsyncIterator[Database]:
    db = initialize_database()
    try:
        await db.init_db()
        yield db
    finally:
        await db.engine.dispose()
