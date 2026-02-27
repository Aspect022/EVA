"""
user_service/handlers/user_handler.py
Production code that processes user requests.
"""
import asyncio
from typing import Optional
from database import ConnectionPool, QueryTimeout


class UserHandler:
    """Handles user-related API requests."""

    def __init__(self, pool: ConnectionPool):
        self.pool = pool
        self._cache = {}

    async def get_user(self, user_id: int) -> Optional[dict]:
        """Fetch user by ID from database."""
        # BUG: No cache eviction - memory grows unbounded
        if user_id in self._cache:
            return self._cache[user_id]

        try:
            conn = await self.pool.acquire(timeout=5.0)
            try:
                # BUG: SELECT * fetches all columns including large BLOB fields
                result = await conn.fetch_one(
                    "SELECT * FROM users WHERE id = $1", user_id
                )
                if result:
                    self._cache[user_id] = dict(result)
                return dict(result) if result else None
            finally:
                await self.pool.release(conn)

        except QueryTimeout:
            raise
        except Exception as e:
            # BUG: Silently swallowing connection pool errors
            print(f"Error fetching user {user_id}: {e}")
            return None

    async def process_batch(self, user_ids: list) -> list:
        """Process a batch of user lookups."""
        # BUG: No concurrency limit - can exhaust connection pool
        tasks = [self.get_user(uid) for uid in user_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]


if __name__ == "__main__":
    # Simulated traceback from production
    raise ConnectionError("Connection pool exhausted")

# --- Actual production traceback ---
# Traceback (most recent call last):
#   File "user_service/main.py", line 45, in handle_request
#     user = await handler.get_user(user_id)
#   File "user_service/handlers/user_handler.py", line 28, in get_user
#     conn = await self.pool.acquire(timeout=5.0)
#   File "database/pool.py", line 112, in acquire
#     raise ConnectionPoolExhausted(f"Pool exhausted: {self.size}/{self.max_size} connections in use")
# ConnectionPoolExhausted: Pool exhausted: 50/50 connections in use
