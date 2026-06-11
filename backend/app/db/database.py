import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from supabase import create_async_client, AsyncClient

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

_client: AsyncClient | None = None


async def get_supabase() -> AsyncGenerator[AsyncClient, None]:
    global _client
    if _client is None:
        _client = await create_async_client(SUPABASE_URL, SUPABASE_KEY)
    yield _client
