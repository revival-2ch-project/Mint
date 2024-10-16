import os

import asyncpg
import dotenv

dotenv.load_dotenv()


class DatabaseService:
    pool: asyncpg.Pool = None

    @classmethod
    async def connect(cls):
        cls.pool = await asyncpg.create_pool(os.getenv("dsn"), statement_cache_size=0)
