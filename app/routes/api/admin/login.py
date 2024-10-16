import bcrypt
import dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ....services.database import DatabaseService
from ....services.admin import AdminPanelSessionService

dotenv.load_dotenv()

router = APIRouter()


class LoginUserModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=16)
    password: str


@router.post("/api/admin/login")
async def requestAdminAccount(model: LoginUserModel):
    user = await DatabaseService.pool.fetchrow(
        "SELECT * FROM admin_panel_users WHERE username = $1", model.username
    )
    if not user:
        raise HTTPException(status_code=403)
    if not bcrypt.checkpw(model.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=403)
    session_id = await AdminPanelSessionService.login(model.username)
    return {
        "detail": "success",
        "session": session_id,
    }
