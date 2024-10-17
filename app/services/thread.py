from typing import Optional, List

from ..objects import Thread
from .database import DatabaseService


class ThreadService:
    @classmethod
    async def getThread(cls, board: str, threadId: int) -> Optional[Thread]:
        """スレッドを取得します。

        Args:
            board (str): 板のID。
            threadId (str): スレッドのID。

        Returns:
            Optional[Thread]: スレッド一覧
        """
        row = await DatabaseService.pool.fetch(
            "SELECT * FROM threads WHERE board = $1 AND id = $2", board, threadId
        )
        if not row:
            return None
        return Thread.model_validate(dict(row))

    @classmethod
    async def getThreads(cls, board: str) -> Optional[List[Thread]]:
        """スレッドの一覧を取得します。

        Args:
            board (str): 板のID。

        Returns:
            Optional[List[Thread]]: スレッド一覧
        """
        rows = await DatabaseService.pool.fetch(
            "SELECT * FROM threads WHERE board = $1 ORDER BY created_at DESC", board
        )
        if not rows:
            return []
        threads = []
        for row in rows:
            threads.append(Thread.model_validate(dict(row)))
        return threads
