from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import func, select

from app.core import Database


class SessionMessageRepository:
    def __init__(self, db: Database):
        self.db = db
        self.table = db.tables["session_messages"]

    async def get_conversation_history(self, session_id: str) -> list[dict[str, str]]:
        table = self.table
        stmt = (
            select(table.c.role, table.c.content)
            .where(table.c.session_id == session_id)
            .order_by(table.c.sequence_number)
        )
        async with self.db.engine.connect() as conn:
            result = await conn.execute(stmt)
            rows = result.fetchall()

        return [{"role": row.role, "content": row.content} for row in rows]

    async def get_next_sequence_number(self, session_id: str) -> int:
        table = self.table
        stmt = select(func.coalesce(func.max(table.c.sequence_number), 0)).where(
            table.c.session_id == session_id
        )
        async with self.db.engine.connect() as conn:
            result = await conn.execute(stmt)
            max_seq = result.scalar_one()
        return max_seq + 1

    async def save_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        sequence_number: int,
        content: str,
        model: str | None = None,
    ) -> None:
        table = self.table
        stmt = table.insert().values(
            id=str(uuid4()),
            user_id=user_id,
            session_id=session_id,
            role=role,
            sequence_number=sequence_number,
            content=content,
            model=model,
            created_at=datetime.now(tz=UTC),
        )
        async with self.db.engine.begin() as conn:
            await conn.execute(stmt)
