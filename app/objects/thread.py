from datetime import datetime

from pydantic import BaseModel


class Thread(BaseModel):
    id: int
    board: str
    title: str
    name: str
    account_id: str
    created_at: datetime
    content: str
    count: int = 1
