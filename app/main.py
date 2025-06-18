from fastapi import FastAPI
from app.api.prices import router
from app.core.limiter import limiter
from app.core.logging_config import setup_logging
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware, _rate_limit_exceeded_handler
from app.core.redis import close_redis, setup_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This function runs when the application starts.
    # It connects to Redis and initializes the cache.
    setup_logging()
    await setup_redis()
    yield
    await close_redis()

app = FastAPI(
    title="Blockhouse Capital Market Data Service",
    description="A microservice for fetching, processing, and serving market data.",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.include_router(router)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Market Data API"}

