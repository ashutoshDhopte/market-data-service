from datetime import datetime

from pydantic import BaseModel, Field


class PriceLatest(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    provider: str


class PollRequest(BaseModel):
    symbols: list[str]
    interval: int
    provider: str = "yfinance"  # Default provider


class PollResponse(BaseModel):
    job_id: str
    status: str
    config: dict

class RateLimitError(BaseModel):
    detail: str = Field(..., example="Rate limit exceeded: 5 per minute")
    error_message: str = Field(..., example="Too many requests. Please try again later.")
