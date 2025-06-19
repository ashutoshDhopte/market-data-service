import json
from typing import Final

import fastapi
import structlog
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.kafka_config import get_kafka_producer
from app.core.limiter import limiter
from app.core.redis import get_redis_pool
from app.schemas.price import PollRequest, PollResponse, PriceLatest, RateLimitError
from app.services import crud, market_provider

router = fastapi.APIRouter(prefix="/prices", tags=["Prices"])

TOPIC: Final[str] = "price-events"
logger = structlog.get_logger(__name__)


@router.get(
    "/latest",
    response_model=PriceLatest,
    responses={
        429: {
            "model": RateLimitError,
            "description": "Rate limit exceeded. The client has sent too many requests in a given amount of time.",
            "headers": {
                "Retry-After": {
                    "description": "The number of seconds to wait before making a new request.",
                    "schema": {"type": "integer"},
                }
            },
        }
    },
)
@limiter.limit("5/minute")
async def get_latest_price(
    request: fastapi.Request,
    symbol: str,
    provider_name: str = "yfinance",
    db: Session = fastapi.Depends(get_db),
    redis: Redis = fastapi.Depends(get_redis_pool),
):
    cache_key = f"price:{symbol}:{provider_name}"
    cached_price = await redis.get(cache_key)

    if cached_price:
        logger.info(
            "CACHE HIT: Returning cached data", symbol=symbol, provider=provider_name
        )
        return json.loads(cached_price)

    logger.info(
        "CACHE MISS: Fetching latest data", symbol=symbol, provider=provider_name
    )

    try:
        provider_service = market_provider.get_provider(provider_name)
    except ValueError as e:
        logger.error(
            "Failed to get market provider",
            provider=provider_name,
            error=str(e),
            exc_info=True,
        )
        raise fastapi.HTTPException(status_code=400, detail=str(e))

    price_data = provider_service.get_latest_price(symbol)
    if not price_data:
        logger.error(
            "Price data not found", symbol=symbol, provider=provider_name, exc_info=True
        )
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"""Price data for symbol '{symbol}' not found
            from provider '{provider_name}'.""",
        )

    raw_response = crud.create_raw_response(
        db=db, symbol=symbol, provider=provider_name, response_data=price_data
    )
    processed_price = crud.create_processed_price(
        db=db, raw_response=raw_response, price=price_data["price"]
    )
    db.commit()

    producer = get_kafka_producer()
    message = {
        "symbol": processed_price.symbol,
        "price": processed_price.price,
        "timestamp": processed_price.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": provider_name,
        "raw_response_id": str(raw_response.id),
    }
    producer.produce(
        TOPIC, key=message["symbol"], value=json.dumps(message).encode("utf-8")
    )
    producer.flush()

    response_data = PriceLatest(
        symbol=processed_price.symbol,
        price=processed_price.price,
        timestamp=processed_price.timestamp,
        provider=processed_price.provider,
    )

    await redis.set(cache_key, response_data.model_dump_json(), ex=60)

    return response_data


@router.post(
    "/poll", status_code=fastapi.status.HTTP_202_ACCEPTED, response_model=PollResponse
)
@limiter.limit("10/minute")
async def poll_prices(
    request: fastapi.Request,
    poll_req: PollRequest,
    background_tasks: fastapi.BackgroundTasks,
    db: Session = fastapi.Depends(get_db),
):
    price_poll_config_id = crud.create_price_poll(
        db,
        symbols=poll_req.symbols,
        interval=poll_req.interval,
        provider=poll_req.provider,
    )
    db.commit()

    return {
        "job_id": f"poll_{price_poll_config_id}",
        "status": "accepted",
        "config": {"symbols": poll_req.symbols, "interval": poll_req.interval},
    }
