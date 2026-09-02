#!/usr/bin/env python3
"""Verify the separate reference publisher/consumer against real RabbitMQ."""

from __future__ import annotations

from importlib.metadata import version
import json
from pathlib import Path
import sys
import time


TASK_ROOT = Path(__file__).resolve().parents[1]
REFERENCE = TASK_ROOT / "reference"
sys.dont_write_bytecode = True
sys.path.insert(0, str(REFERENCE))

import common  # noqa: E402
import consumer  # noqa: E402
import producer  # noqa: E402


def get_one(channel):
    for _ in range(40):
        method, properties, body = channel.basic_get(
            queue=common.QUEUE_NAME,
            auto_ack=False,
        )
        if method is not None:
            return method, properties, body
        time.sleep(0.05)
    raise TimeoutError("message was not ready within two seconds")


def decode(properties, body: bytes) -> dict[str, str]:
    payload = json.loads(body)
    assert payload["message_id"] == properties.message_id
    return payload


def main() -> int:
    assert version("pika") == "1.4.4"

    setup_connection = common.open_connection()
    try:
        setup_channel = setup_connection.channel()
        common.declare_queue(setup_channel)
        setup_channel.queue_purge(queue=common.QUEUE_NAME)
    finally:
        setup_connection.close()

    baseline = producer.publish(
        "baseline-caption-001",
        "caption-video",
        "video-42",
    )
    consumed = consumer.consume_one()
    assert consumed["message_id"] == baseline["message_id"]
    assert consumed["redelivered"] is False
    assert consumed["acknowledged"] is True
    print("BASELINE same_message=true redelivered=false ack=true")

    variation = producer.publish(
        "redelivery-caption-001",
        "caption-video",
        "video-84",
    )
    first_connection = common.open_connection()
    first_channel = first_connection.channel()
    common.declare_queue(first_channel)
    method_1, properties_1, body_1 = get_one(first_channel)
    first_payload = decode(properties_1, body_1)
    assert first_payload == variation
    assert method_1.redelivered is False
    print(
        "VARIATION_FIRST id=redelivery-caption-001 "
        "redelivered=false ack=withheld action=close-connection"
    )
    # Closing the delivery's connection without basic_ack is the controlled failure.
    first_connection.close()

    second_connection = common.open_connection()
    try:
        second_channel = second_connection.channel()
        common.declare_queue(second_channel)
        method_2, properties_2, body_2 = get_one(second_channel)
        second_payload = decode(properties_2, body_2)
        assert second_payload == first_payload
        assert properties_2.message_id == properties_1.message_id
        assert body_2 == body_1
        assert method_2.redelivered is True
        second_channel.basic_ack(delivery_tag=method_2.delivery_tag)
        print(
            "VARIATION_REDELIVERY id=redelivery-caption-001 "
            "same_message=true redelivered=true ack=true"
        )
        after_ack = second_channel.queue_declare(
            queue=common.QUEUE_NAME,
            passive=True,
        )
        assert after_ack.method.message_count == 0
    finally:
        second_connection.close()

    # Observe final topology on a fresh connection so consumer cancellation
    # from the baseline callback has reached the broker before we assert it.
    final_connection = common.open_connection()
    try:
        final_channel = final_connection.channel()
        for _ in range(40):
            final = final_channel.queue_declare(
                queue=common.QUEUE_NAME,
                passive=True,
            )
            if final.method.consumer_count == 0:
                break
            time.sleep(0.05)
        assert final.method.message_count == 0
        assert final.method.consumer_count == 0
        print("FINAL_QUEUE ready=0 consumers=0")
    finally:
        final_connection.close()

    print("SD-BEG-140-T01_REFERENCE_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
