from fastapi import APIRouter

from ....services.database import DatabaseService
from ....objects import Board

router = APIRouter()


@router.get("/api/boards")
async def boardsList():
    """
    板の一覧をJSONで返します。
    """

    rows = await DatabaseService.pool.fetch("SELECT * FROM boards")
    if not rows:
        return []
    boards = []
    for row in rows:
        boards.append(Board.model_validate(dict(row)))
    return boards
