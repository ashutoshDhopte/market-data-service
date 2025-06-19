from confluent_kafka import Producer


def get_kafka_producer():
    producer_conf = {"bootstrap.servers": "kafka:29092"}
    # producer_conf = {'bootstrap.servers': 'localhost:9092'}
    return Producer(producer_conf)
