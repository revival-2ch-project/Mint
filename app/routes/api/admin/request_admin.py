import os

import bcrypt
import dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ....services.database import DatabaseService
from ....services.admin import AdminPanelSessionService

dotenv.load_dotenv()

router = APIRouter()


class AdminUserRequestModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=16)
    password: str
    adminRequestPassWord: str


@router.post("/api/admin/request")
async def requestAdminAccount(model: AdminUserRequestModel):
    users = await DatabaseService.pool.fetch("SELECT * FROM admin_panel_users")
    if users:
        raise HTTPException(status_code=403)
    if model.adminRequestPassWord != os.getenv("admin_request_password"):
        raise HTTPException(status_code=403)
    salt = bcrypt.gensalt(rounds=10, prefix=b"2a")
    model.password = bcrypt.hashpw(model.password.encode(), salt).decode()
    await DatabaseService.pool.execute(
        "INSERT INTO admin_panel_users (username, password, permissions) values($1, $2, $3)",
        model.username,
        model.password,
        8,
    )
    session_id = await AdminPanelSessionService.login(model.username)
    return {
        "detail": "success",
        "session": session_id,
    }
