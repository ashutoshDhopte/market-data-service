from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from app.schemas.price import PriceLatest, PollRequest, PollResponse
from app.services import crud
from app.services import market_provider
from sqlalchemy.orm import Session
from app.core.db import get_db
import uuid

router = APIRouter(
    prefix="/prices",
    tags=["Prices"]
)

def poll_market_data_task(symbol: str, provider: str):
    print(f"Polling data for {symbol} from {provider}...")

@router.get("/latest", response_model=PriceLatest)
async def get_latest_price(symbol: str, provider_name: str = "yfinance", db: Session = Depends(get_db)):
    """
    Fetches the latest price for a symbol.
    1. Fetches data from the external market provider.
    2. Stores the raw response in the database.
    3. Stores the processed price point in the database.
    4. Returns the processed price.
    """
    # Step 1: Get the market data provider service
    try:
        provider_service = market_provider.get_provider(provider_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Step 2: Fetch data from the external API
    price_data = provider_service.get_latest_price(symbol)
    if not price_data:
        raise HTTPException(status_code=404, detail=f"Price data for symbol '{symbol}' not found from provider '{provider_name}'.")
    
    # Step 3: Store the raw response using the CRUD service
    raw_response = crud.create_raw_response(db=db, symbol=symbol, provider=provider_name, response_data=price_data)

    # Step 4: Store the processed price using the CRUD service
    processed_price = crud.create_processed_price(db=db, raw_response=raw_response, price=price_data['price'])

    db.commit()

    # Step 5: Return the data in the correct API schema format
    return PriceLatest(
        symbol=processed_price.symbol,
        price=processed_price.price,
        timestamp=processed_price.timestamp,
        provider=processed_price.provider
    )

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