#!/usr/bin/env python3
"""Learner starter: publish one deterministic task to RabbitMQ."""

from __future__ import annotations

import json

import pika


HOST = "127.0.0.1"
PORT = 5678
VHOST = "sd_beg_140"
USERNAME = "learner"
PASSWORD = "local-only-demo"
QUEUE_NAME = "sd_beg_140_tasks"


def main() -> int:
    parameters = pika.ConnectionParameters(
        host=HOST,
        port=PORT,
        virtual_host=VHOST,
        credentials=pika.PlainCredentials(USERNAME, PASSWORD),
    )
    connection = pika.BlockingConnection(parameters)
    try:
        channel = connection.channel()
        message = {
            "message_id": "rahul-task-001",
            "kind": "caption-video",
            "video_id": "video-42",
        }

        # TODO 1: Declare the exact durable queue and choose its queue type.
        # TODO 2: Enable publisher confirms before claiming broker acceptance.
        # TODO 3: Publish this JSON to the queue with a persistent message mode.
        # TODO 4: Print narrow evidence: ID, route, and confirm result.
        raise NotImplementedError(
            "Complete the declaration, confirm, and publish steps without opening reference/."
        )
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
