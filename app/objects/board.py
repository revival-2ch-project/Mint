from pydantic import BaseModel


class Board(BaseModel):
    id: str
    name: str
    anonymous_name: str = "名無しさん"
    deleted_name: str = "あぼーん"
    subject_count: int = 64
    name_count: int = 50
    message_count: int = 2000
