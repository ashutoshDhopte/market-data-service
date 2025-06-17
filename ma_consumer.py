import json
import socket
import time
from confluent_kafka import Consumer, KafkaError

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
            price = event['price']
            print(f"Consumed event for {symbol}: {price}")

            # 1. Fetch the last 4 prices for the symbol from the DB.
            # 2. Append the new price to the list.
            # 3. Calculate the 5-point moving average.
            # 4. Upsert the result into the `symbol_averages` table.

    finally:
        consumer.close()

if __name__ == "__main__":
    run_consumer()