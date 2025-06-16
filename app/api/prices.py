from fastapi import APIRouter, status, BackgroundTasks
from app.schemas.price import PriceLatest, PollRequest, PollResponse
import uuid

router = APIRouter(
    prefix="/prices",
    tags=["Prices"]
)

def poll_market_data_task(symbol: str, provider: str):
    print(f"Polling data for {symbol} from {provider}...")

@router.get("/latest", response_model=PriceLatest)
async def get_latest_price(symbol: str, provider: str = "alpha_vantage"):
    return {
        "symbol": symbol,
        "price": 150.25,
        "timestamp": "2024-03-20T10:30:00Z",
        "provider": provider
    }

@router.post("/poll", status_code=status.HTTP_202_ACCEPTED, response_model=PollResponse)
async def poll_prices(request: PollRequest, background_tasks: BackgroundTasks):
    job_id = f"poll_{uuid.uuid4()}"
    # Use background tasks to start the polling without blocking the response.
    for symbol in request.symbols:
         background_tasks.add_task(poll_market_data_task, symbol, request.provider)

    return {
        "job_id": job_id,
        "status": "accepted",
        "config": {
            "symbols": request.symbols,
            "interval": request.interval
        }
    }