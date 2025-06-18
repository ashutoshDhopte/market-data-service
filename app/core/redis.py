import os
from redis.asyncio import Redis

redis_pool: Redis = None

def get_redis_pool():
    """
    Dependency function to get the Redis connection pool.
    """
    return redis_pool

async def setup_redis():
    """
    Initializes the Redis connection pool. To be called at application startup.
    """
    global redis_pool
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    redis_pool = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    print("Redis connection pool initialized.")

async def close_redis():
    """
    Closes the Redis connection pool. To be called at application shutdown.
    """
    if redis_pool:
        await redis_pool.close()
        print("Redis connection pool closed.")