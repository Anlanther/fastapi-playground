import asyncio
import json
import uuid
from typing import AsyncGenerator

from sqlalchemy import text

from app.core import Database
from app.dependencies.llm_client import get_llm_client
from app.models import (
    LogResponse,
    TextResponse,
    ThinkResponse,
)
from app.services.token_estimator import estimate_tokens


class ReactService:
    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.llm = get_llm_client()

    async def stream_review(
        self,
        book_title: str,
        book_author: str | None,
        session_id: str | None,
        db: Database,
        user_message: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Produce a stream of AgentResponse-like payloads while persisting
        every message to `session_messages`.

        - Save the initial user message (if present)
        - Stream model output; save each chunk as an agent message
        - Emit a LogResponse checkpoint with a span_id and wait for approval
        """

        sid = session_id or "default"

        # persist user's initial message
        if user_message:
            async with db.engine.begin() as conn:
                await conn.execute(
                    text(
                        "INSERT INTO session_messages (session_id, role, span_id, approved, payload, tokens_estimate) VALUES (:session_id, :role, :span_id, :approved, :payload, :tokens_estimate)"
                    ),
                    {
                        "session_id": sid,
                        "role": "user",
                        "span_id": None,
                        "approved": None,
                        "payload": user_message,
                        "tokens_estimate": estimate_tokens(user_message),
                    },
                )

        # If LLM client provides streaming, prefer it. Otherwise use mock sequence.
        try:
            # assume llm.stream yields JSON-like strings or text chunks
            async for chunk in self.llm.stream(f"Write a short book review for {book_title} by {book_author or 'Unknown'}"):
                payload = chunk if isinstance(
                    chunk, str) else json.dumps(chunk)
                # persist agent chunk
                async with db.engine.begin() as conn:
                    await conn.execute(
                        text(
                            "INSERT INTO session_messages (session_id, role, span_id, approved, payload, tokens_estimate) VALUES (:session_id, :role, :span_id, :approved, :payload, :tokens_estimate)"
                        ),
                        {
                            "session_id": sid,
                            "role": "agent",
                            "span_id": None,
                            "approved": None,
                            "payload": payload,
                            "tokens_estimate": estimate_tokens(payload),
                        },
                    )
                yield payload + "\n"
                await asyncio.sleep(self.delay)
        except Exception:
            # fallback simple mock stream
            sequence = [
                ThinkResponse(text="Thinking about the book..."),
                TextResponse(
                    text=f"{book_title} by {book_author or 'Unknown'}\n\n"),
                TextResponse(text="Summary: "),
                TextResponse(text="The book explores themes of ... "),
            ]
            for item in sequence:
                payload = json.dumps(item.model_dump(mode="json"))
                async with db.engine.begin() as conn:
                    await conn.execute(
                        text(
                            "INSERT INTO session_messages (session_id, role, span_id, approved, payload, tokens_estimate) VALUES (:session_id, :role, :span_id, :approved, :payload, :tokens_estimate)"
                        ),
                        {
                            "session_id": sid,
                            "role": "agent",
                            "span_id": None,
                            "approved": None,
                            "payload": payload,
                            "tokens_estimate": estimate_tokens(payload),
                        },
                    )
                yield payload + "\n"
                await asyncio.sleep(self.delay)

        # create an approval checkpoint
        span_id = str(uuid.uuid4())
        async with db.engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO session_messages (session_id, role, span_id, approved, payload, tokens_estimate) VALUES (:session_id, :role, :span_id, :approved, :payload, :tokens_estimate)"
                ),
                {
                    "session_id": sid,
                    "role": "system",
                    "span_id": span_id,
                    "approved": False,
                    "payload": json.dumps({"reason": "awaiting user approval"}),
                    "tokens_estimate": None,
                },
            )

        # Emit a LogResponse indicating a pause for approval
        log = LogResponse(span_id=span_id)
        payload = json.dumps(log.model_dump(mode="json"))
        async with db.engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO session_messages (session_id, role, span_id, approved, payload, tokens_estimate) VALUES (:session_id, :role, :span_id, :approved, :payload, :tokens_estimate)"
                ),
                {
                    "session_id": sid,
                    "role": "agent",
                    "span_id": span_id,
                    "approved": False,
                    "payload": payload,
                    "tokens_estimate": estimate_tokens(payload),
                },
            )
        yield payload + "\n"

        # Poll the DB until approved
        approved = False
        while not approved:
            async with db.engine.connect() as conn:
                result = await conn.execute(
                    text(
                        "SELECT approved FROM session_messages WHERE session_id = :session_id AND span_id = :span_id AND approved IS NOT NULL ORDER BY id DESC LIMIT 1"
                    ),
                    {"session_id": sid, "span_id": span_id},
                )
                row = result.first()
                if row is not None and row[0] is True:
                    approved = True
                    break
            await asyncio.sleep(0.5)

        # After approval, continue streaming final text
        final = [TextResponse(text="User approved. Continuing..."), TextResponse(
            text="Final short review: A compelling read.")]
        for item in final:
            payload = json.dumps(item.model_dump(mode="json"))
            async with db.engine.begin() as conn:
                await conn.execute(
                    text(
                        "INSERT INTO session_messages (session_id, role, span_id, approved, payload, tokens_estimate) VALUES (:session_id, :role, :span_id, :approved, :payload, :tokens_estimate)"
                    ),
                    {
                        "session_id": sid,
                        "role": "agent",
                        "span_id": None,
                        "approved": None,
                        "payload": payload,
                        "tokens_estimate": estimate_tokens(payload),
                    },
                )
            yield payload + "\n"
            await asyncio.sleep(self.delay)
