import os
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.api import prices
from redis import asyncio as aioredis
from app.core.logging_config import setup_logging
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This function runs when the application starts.
    # It connects to Redis and initializes the cache.
    setup_logging()
    redis_url = os.getenv("REDIS_URL", "redis://localhost")
    redis = aioredis.from_url(redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    print("Connected to Redis and initialized cache.")
    yield

app = FastAPI(
    title="Blockhouse Capital Market Data Service",
    description="A microservice for fetching, processing, and serving market data.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(prices.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Market Data API"}

