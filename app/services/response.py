from typing import Optional, List

from ..objects import Response
from .database import DatabaseService


class ResponseService:
    @classmethod
    async def getResponses(cls, board: str, thread_id: int) -> Optional[List[Response]]:
        """スレッドについたレスの一覧を返します。

        Args:
            board (str): 板のID。
            thread_id (int): スレッドのID。

        Returns:
            Optional[List[Response]]: レス一覧
        """
        rows = await DatabaseService.pool.fetch(
            "SELECT * FROM responses WHERE board = $1 AND thread_id = $2 ORDER BY created_at DESC",
            board,
            thread_id,
        )
        if not rows:
            return []
        responses = []
        for row in rows:
            responses.append(Response.model_validate(dict(row)))
        return responses
