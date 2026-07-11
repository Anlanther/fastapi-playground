from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from app.dependencies.database import get_db

router = APIRouter(tags=["Health"])


async def check_database_readiness(db=Depends(get_db)) -> None:
    try:
        async with db.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail="database unavailable") from exc


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(_: None = Depends(check_database_readiness)) -> dict[str, str]:
    return {"status": "ready"}
