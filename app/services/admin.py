import random
import string
from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException

from .database import DatabaseService


class AdminPanelSessionService:
    @classmethod
    async def sessionCheck(cls, x_mint_session: str = Header(...)):
        if not x_mint_session:
            raise HTTPException(status_code=403)
        session = await cls.validateSession(x_mint_session)
        if not session:
            raise HTTPException(status_code=403)
        return session

    @classmethod
    def randomID(cls, n: int = 10) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    @classmethod
    async def login(cls, username: str, session_duration: int = 3600) -> str:
        sessionId = cls.randomID(10)
        expire_at = datetime.now(timezone.utc) + timedelta(seconds=session_duration)
        await DatabaseService.pool.execute(
            """
            INSERT INTO admin_panel_sessions(id, username, expire_at) VALUES($1, $2, $3)
        """,
            sessionId,
            username,
            expire_at,
        )
        return sessionId

    @classmethod
    async def validateSession(
        cls, session_id: str, session_duration: int = 3600
    ) -> dict:
        session = await DatabaseService.pool.fetchrow(
            """
            SELECT * FROM admin_panel_sessions WHERE id = $1
        """,
            session_id,
        )

        if not session:
            return False

        session = dict(session)

        if session["expire_at"] < datetime.now(timezone.utc):
            await cls.logout(session_id)
            return False

        expire_at = datetime.now(timezone.utc) + timedelta(seconds=session_duration)
        await DatabaseService.pool.execute(
            "UPDATE admin_panel_sessions SET expire_at = $1 WHERE id = $2",
            expire_at,
            session["id"],
        )

        session["user"] = await DatabaseService.pool.fetchrow(
            """
            SELECT * FROM admin_panel_users WHERE username = $1
            """,
            session["username"],
        )

        return session

    @classmethod
    async def logout(cls, session_id: str) -> None:
        await DatabaseService.pool.execute(
            """
            DELETE FROM admin_panel_sessions WHERE id = $1
        """,
            session_id,
        )
