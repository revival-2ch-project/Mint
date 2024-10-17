import asyncpg
import dotenv
from fastapi import APIRouter, Depends

from .....objects import ChangeableMetaData, CaptchaType
from .....services.admin import AdminPanelSessionService
from .....services.database import DatabaseService

dotenv.load_dotenv()

router = APIRouter()


@router.patch("/api/admin/meta/edit")
async def createBoard(
    meta: ChangeableMetaData,
    session: dict = Depends(AdminPanelSessionService.sessionCheck),
):
    """板を作成します。"""

    data = meta.model_dump()

    set_clauses = []
    values = [data["id"]]
    idx = 2

    for key, value in data.items():
        if key == "id":
            continue
        if value is None:
            set_clauses.append(f"{key} = DEFAULT")
        else:
            set_clauses.append(f"{key} = ${idx}")
            if isinstance(value, CaptchaType):
                values.append(value.value)
            else:
                values.append(value)
            idx += 1

    query = f"""
    UPDATE meta
    SET {', '.join(set_clauses)}
    WHERE id = $1
    """

    await DatabaseService.pool.execute(query, *values)
    return {"detail": "success"}
