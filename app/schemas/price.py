from datetime import datetime

from pydantic import BaseModel


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
