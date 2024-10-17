from typing import Optional

from ..objects import Board
from .database import DatabaseService


class BoardService:
    @classmethod
    async def getBoard(cls, id: str) -> Optional[Board]:
        row = await DatabaseService.pool.fetchrow(
            "SELECT * FROM boards WHERE id = $1", id
        )
        if not row:
            return None
        return Board.model_validate(dict(row))
