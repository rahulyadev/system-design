#!/usr/bin/env python3
"""Reference publisher with a persistent message and publisher confirm."""

from __future__ import annotations

import argparse
import json

import pika

from common import QUEUE_NAME, declare_queue, open_connection


def publish(message_id: str, kind: str, video_id: str) -> dict[str, str]:
    message = {
        "kind": kind,
        "message_id": message_id,
        "video_id": video_id,
    }
    body = json.dumps(message, sort_keys=True, separators=(",", ":")).encode()
    connection = open_connection()
    try:
        channel = connection.channel()
        declare_queue(channel)
        channel.confirm_delivery()
        # In Pika's blocking adapter, confirm mode waits for Basic.Ack and
        # raises NackError or UnroutableError on failure. A successful call
        # returns None, so absence of those exceptions is the positive proof.
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
                message_id=message_id,
                type=kind,
            ),
            mandatory=True,
        )
        print(
            f"PUBLISHED id={message_id} queue={QUEUE_NAME} "
            "confirm=true delivery_mode=persistent"
        )
        return message
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--message-id", default="reference-task-001")
    parser.add_argument("--kind", default="caption-video")
    parser.add_argument("--video-id", default="video-42")
    args = parser.parse_args()
    publish(args.message_id, args.kind, args.video_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
