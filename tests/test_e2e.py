from datetime import datetime
import os
import time
import httpx
import pytest
import pytest_asyncio
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# --- Test Configuration ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("""DATABASE_URL environment variable is not set. Make sure .env file is present.""")

API_BASE_URL = "http://localhost:8000"

# How long the test should wait for the async consumer to finish (in seconds)
POLL_TIMEOUT = 15
# How often to check the database while polling
POLL_INTERVAL = 1

# --- Database Setup for Test ---
# We connect directly to the database to verify results
engine = sqlalchemy.create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define SQLAlchemy models to interact with the tables
Base = sqlalchemy.orm.declarative_base()


class ProcessedPrice(Base):
    __tablename__ = "processed_prices"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    symbol = sqlalchemy.Column(sqlalchemy.String, index=True)
    price = sqlalchemy.Column(sqlalchemy.Float(precision=2))
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now, index=True)
    provider = sqlalchemy.Column(sqlalchemy.String)
    raw_response_id = sqlalchemy.Column(sqlalchemy.Integer)


class SymbolAverage(Base):
    __tablename__ = "symbol_averages"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    symbol = sqlalchemy.Column(sqlalchemy.String, unique=True)
    moving_average = sqlalchemy.Column(sqlalchemy.Float(precision=2))
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)


# --- Pytest Fixtures and Test Functions ---


@pytest.fixture(scope="module")
def db_session():
    """Pytest fixture to provide a database session for the test module."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest_asyncio.fixture(scope="function")
async def http_client():
    """
    Pytest fixture to provide an httpx AsyncClient.
    """
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        yield client


@pytest.mark.asyncio
async def test_full_data_pipeline(http_client: httpx.AsyncClient, db_session):
    """
    Tests the entire data pipeline from API fetch to moving average storage.
    Prerequisites: All services (API, DB, Kafka, Zookeeper) and the
                   ma_consumer.py script must be running.
    """
    test_symbol = "MSFT"
    print(f"--- Running E2E pipeline test for symbol: {test_symbol} ---")

    # === 1. TRIGGER: Call the API to fetch the price ===
    # We add a cache_buster to ensure we don't get a cached response
    trigger_url = f"/prices/latest?symbol={test_symbol}&provider_name=yfinance"
    response = await http_client.get(trigger_url)

    # Basic check that the API call was successful
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["symbol"] == test_symbol
    print(f"""Step 1 PASSED: API call successful, received price {response_data['price']}.""")

    # === 2. VERIFY INITIAL DB STORAGE ===
    # Check that the raw price was stored in the `processed_prices` table
    # Give it a moment to ensure the transaction has committed
    time.sleep(1)
    price_record = (db_session.query(ProcessedPrice).filter_by(symbol=test_symbol).first())
    assert price_record is not None
    assert price_record.symbol == test_symbol
    print("Step 2 PASSED: Initial price record found in the database.")

    # === 3. VERIFY FINAL MA STORAGE (KAFKA CONSUMER RESULT) ===
    start_time = time.time()
    ma_record = None
    while time.time() - start_time < POLL_TIMEOUT:
        ma_record = (
            db_session.query(SymbolAverage).filter_by(
                symbol=test_symbol
            ).first()
        )
        if ma_record:
            break
        print(f"""Polling... waiting for MA record for {test_symbol} (elapsed: {time.time() - start_time:.0f}s)""")
        time.sleep(POLL_INTERVAL)

    # The test fails if the consumer didn't store the moving average in time
    assert (
        ma_record is not None
    ), f"""TIMEOUT: MA record for {test_symbol} not found after {POLL_TIMEOUT} seconds."""
    assert ma_record.symbol == test_symbol
    assert ma_record.moving_average is not None
    print(f"""Step 3 PASSED: Moving average record found in database (MA: {ma_record.moving_average}).""")
    print("--- E2E pipeline test successful! ---")
