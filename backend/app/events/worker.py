"""Local Kafka workers: ack broker only after durable, duplicate-safe processing."""

import argparse
import os
import time

from app.events import outbox  # noqa: F401
from app.events.pipeline import TOPIC, consume, publish_one, work_one


def main():
    from app.logging import configure_logging

    configure_logging()
    from app.telemetry import configure

    configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["publisher", "projection", "proactive", "audit", "jobs"])
    args = parser.parse_args()
    from kafka import KafkaConsumer, KafkaProducer

    broker = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    if args.mode == "publisher":
        producer = KafkaProducer(
            bootstrap_servers=broker,
            acks="all",
            retries=3,
            max_block_ms=10000,
            request_timeout_ms=10000,
        )
        while True:
            if not publish_one(
                lambda key, value: producer.send(TOPIC, key=key, value=value).get(timeout=10)
            ):
                time.sleep(0.25)
    elif args.mode == "jobs":
        while True:
            if not work_one():
                time.sleep(0.5)
    else:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=broker,
            group_id="nova-" + args.mode + "-v1",
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            max_poll_records=1,
        )
        for message in consumer:
            consume(message.value, args.mode)
            consumer.commit()


if __name__ == "__main__":
    main()
