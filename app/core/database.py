from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine


class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.metadata = MetaData()
        self.tables = {}

    def register_table(self, name: str, table):
        """Register a table with the database."""
        self.tables[name] = table

    async def init_db(self):
        """Initialize database tables on startup."""
        async with self.engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)
