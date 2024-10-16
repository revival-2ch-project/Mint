import random, string
from datetime import datetime, timedelta

from .database import DatabaseService


class AdminPanelSessionService:
    @classmethod
    def randomID(cls, n: int = 10) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=n))

    @classmethod
    async def login(cls, username: str, session_duration: int = 3600) -> str:
        sessionId = cls.randomID(10)
        expire_at = datetime.now() + timedelta(seconds=session_duration)
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
    async def validate_session(cls, session_id: str) -> bool:
        session = await DatabaseService.pool.fetchrow(
            """
            SELECT * FROM admin_panel_sessions WHERE id = $1
        """,
            session_id,
        )

        if not session:
            return False

        if session["expire_at"] < datetime.now():
            await cls.logout(session_id)
            return False

        return True

    @classmethod
    async def logout(cls, session_id: str) -> None:
        await DatabaseService.pool.execute(
            """
            DELETE FROM admin_panel_sessions WHERE id = $1
        """,
            session_id,
        )
