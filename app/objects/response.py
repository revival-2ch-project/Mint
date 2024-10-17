from datetime import datetime

from pydantic import BaseModel


class Response(BaseModel):
    id: int
    thread_id: int
    board: str
    title: str
    name: str
    account_id: str
    created_at: datetime
    content: str
