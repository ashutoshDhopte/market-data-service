import json
import os
import socket
import time
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# The engine is the entry point to the database.
engine = create_engine(DATABASE_URL)

# A SessionLocal class is a factory for new Session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def calculate_moving_average(prices: list[float]) -> float:
    if not prices:
        return 0.0
    return sum(prices) / len(prices)

def wait_for_port(host, port, timeout=30):
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("Service is up!")
                return
        except Exception as e:
            print(e)
            if time.time() - start > timeout:
                raise TimeoutError("Timed out waiting for service")
            time.sleep(1)

def get_last5_price_by_symbol(symbol: str):
    """Retrieves last 5 processed price for a given symbol."""
    db: Session = SessionLocal()
    result = db.execute(
        text("""
            SELECT price
            FROM processed_prices
            WHERE symbol = :symbol
            ORDER BY timestamp DESC
            LIMIT 5
        """),
        {"symbol": symbol}
    ).fetchall()

    return [float(row[0]) for row in result]

def save_symbol_ma(symbol: str, ma: float):
    db: Session = SessionLocal()
    db.execute(
        text("""
            INSERT INTO symbol_averages(symbol, moving_average)
            VALUES (:symbol, :moving_average)
            ON CONFLICT (symbol)
            DO UPDATE SET moving_average = EXCLUDED.moving_average
        """),
        {
            "symbol": symbol,
            "moving_average": ma
        }
    )
    db.commit()


def run_consumer():

    wait_for_port("localhost", 9092, 60)

    consumer_conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'ma_calculators',
        'auto.offset.reset': 'earliest'
    }


    consumer = Consumer(consumer_conf)
    consumer.subscribe(['price-events'])

    print("Consumer is running...")
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print("Topic not found. Waiting...")
                    continue
                else:
                    break

            event = json.loads(msg.value().decode('utf-8'))
            symbol = event['symbol']
            print(f"Consumed event for {symbol}")

            # get last 5 prices
            price_list = get_last5_price_by_symbol(symbol)

            # calculate ma
            ma = calculate_moving_average(price_list)

            # save ma to symbol_average table
            save_symbol_ma(symbol, ma)

    finally:
        consumer.close()

if __name__ == "__main__":
    run_consumer()