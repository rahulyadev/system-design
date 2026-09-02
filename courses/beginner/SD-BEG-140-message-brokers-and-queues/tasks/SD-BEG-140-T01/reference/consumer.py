#!/usr/bin/env python3
"""Reference consumer that processes one delivery before acknowledging it."""

from __future__ import annotations

import json

from common import QUEUE_NAME, declare_queue, open_connection


def consume_one(timeout_seconds: float = 10.0) -> dict[str, object]:
    connection = open_connection()
    received: list[dict[str, object]] = []
    try:
        channel = connection.channel()
        declare_queue(channel)
        channel.basic_qos(prefetch_count=1)

        def on_message(ch, method, properties, body: bytes) -> None:
            payload = json.loads(body)
            if payload.get("message_id") != properties.message_id:
                raise ValueError("body and AMQP message IDs differ")
            record = {
                "message_id": properties.message_id,
                "kind": payload.get("kind"),
                "video_id": payload.get("video_id"),
                "redelivered": bool(method.redelivered),
            }
            # The synthetic business action is the validated record above.
            # Acknowledge only after that action succeeds.
            ch.basic_ack(delivery_tag=method.delivery_tag)
            record["acknowledged"] = True
            received.append(record)
            print(
                f"CONSUMED id={properties.message_id} "
                f"redelivered={str(bool(method.redelivered)).lower()} ack=true"
            )
            ch.stop_consuming()

        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=on_message,
            auto_ack=False,
        )
        timer = connection.call_later(timeout_seconds, channel.stop_consuming)
        channel.start_consuming()
        connection.remove_timeout(timer)
        if not received:
            raise TimeoutError(f"no message arrived within {timeout_seconds} seconds")
        return received[0]
    finally:
        if connection.is_open:
            connection.close()


def main() -> int:
    consume_one()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
