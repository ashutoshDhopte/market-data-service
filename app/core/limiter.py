import os
from slowapi import Limiter
from starlette.requests import Request
from dotenv import load_dotenv
from fastapi import Request
from starlette.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

def get_remote_address_key(request: Request) -> str:
    """
    A key function to identify the client by their remote address.
    Includes a debug print statement to verify it's being called.
    """
    client_host = "unknown"
    if request.client and request.client.host:
        client_host = request.client.host

    # This print statement is our proof that the middleware is running.
    print(f"--- RATE LIMITER KEY FUNC CALLED --- > Client IP: {client_host}")
    
    return client_host

# Initialize the limiter with the correct key function and Redis storage
limiter = Limiter(
    key_func=get_remote_address_key,
    storage_uri=REDIS_URL
)

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for 429 Too Many Requests errors.
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after_seconds": exc.retry_after
        }
    )