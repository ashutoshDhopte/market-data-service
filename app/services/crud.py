import json
from sqlalchemy.orm import Session
from app.models.price import RawResponse, ProcessedPrice, PollingJobConfigs
from typing import Optional

def create_raw_response(db: Session, symbol: str, provider: str, response_data: dict) -> RawResponse:
    """Stores the raw JSON response from the market data provider."""
    db_raw_response = RawResponse(
        symbol=symbol,
        provider=provider,
        data=json.dumps(response_data) # Store data as a JSON string
    )
    db.add(db_raw_response)
    db.flush()
    db.refresh(db_raw_response)
    return db_raw_response

def create_processed_price(db: Session, raw_response: RawResponse, price: float) -> ProcessedPrice:
    """Stores the clean, processed price point."""
    db_processed_price = ProcessedPrice(
        symbol=raw_response.symbol,
        price=float(price),
        provider=raw_response.provider,
        raw_response_id=raw_response.id
    )
    db.add(db_processed_price)
    db.flush()
    db.refresh(db_processed_price)
    return db_processed_price

def get_latest_price_by_symbol(db: Session, symbol: str) -> Optional[ProcessedPrice]:
    """Retrieves the most recent processed price for a given symbol."""
    return db.query(ProcessedPrice).filter(ProcessedPrice.symbol == symbol).order_by(ProcessedPrice.timestamp.desc()).first()

def create_price_poll(db: Session, symbols: list[str], interval: int, provider: str):
    """Creates price polling record"""
    symbols_comma_separated = ",".join(symbols)
    db_polling_job_config = PollingJobConfigs(
        symbols=symbols_comma_separated,
        interval=interval,
        provider=provider
    )
    db.add(db_polling_job_config)
    db.flush()
    db.refresh(db_polling_job_config)
    return db_polling_job_config.id