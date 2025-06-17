from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RawResponse(Base):
    __tablename__ = "raw_responses"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    provider = Column(String)
    data = Column(String) # Store the raw JSON response
    timestamp = Column(DateTime, default=datetime.utcnow)

class ProcessedPrice(Base):
    __tablename__ = "processed_prices"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float(precision=2))  # Limits to 6 decimal places in storage
    timestamp = Column(DateTime, index=True)
    provider = Column(String)
    raw_response_id = Column(Integer)

class SymbolAverage(Base):
    __tablename__ = "symbol_averages"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True)
    moving_average = Column(Float(precision=2))
    updated_at = Column(DateTime, default=datetime.utcnow)

# Add indexes for faster queries
Index('idx_processed_prices_symbol_timestamp', ProcessedPrice.symbol, ProcessedPrice.timestamp.desc())