import os

import bcrypt
import dotenv
from fastapi import APIRouter, HTTPException, Depends

from .....objects import Board
from .....services.admin import AdminPanelSessionService
from .....services.database import DatabaseService
from .....services.board import BoardService

dotenv.load_dotenv()

router = APIRouter()


@router.put("/api/admin/boards")
async def createBoard(
    board: Board, session: dict = Depends(AdminPanelSessionService.sessionCheck)
):
    """板を作成します。"""
    if await BoardService.getBoard(board.id):
        raise HTTPException(status_code=500, detail="Board ID already used")
    await DatabaseService.pool.execute(
        "INSERT INTO boards (id, name, anonymous_name, deleted_name, subject_count, name_count, message_count, head) values ($1, $2, $3, $4, $5, $6, $7, $8)",
        *board.model_dump().values()
    )
    return board
