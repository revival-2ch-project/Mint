import os

import dotenv

from ..objects import MetaData
from .database import DatabaseService

dotenv.load_dotenv()


class FailedToLoadMetaDataException(Exception):
    def __init__(self, message: str = "Failed to load metadata."):
        super().__init__(message)


class MetaDataService:
    metadata: MetaData = None

    @classmethod
    async def load(cls, *, name: str):
        try:
            row = await DatabaseService.pool.fetchrow(
                "SELECT * FROM meta WHERE id = $1", int(os.getenv("metaid"))
            )
            if not row:
                row = await DatabaseService.pool.fetchrow(
                    "INSERT INTO meta (id, name) VALUES ($1, $2) RETURNING *",
                    int(os.getenv("metaid")),
                    name,
                )
            cls.metadata: MetaData = MetaData.model_validate(dict(row))
        except:
            raise FailedToLoadMetaDataException()
