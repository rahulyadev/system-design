#!/usr/bin/env python3
"""Learner starter: consume and explicitly acknowledge one RabbitMQ task."""

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

        # TODO 1: Declare the same queue contract as the producer.
        # TODO 2: Limit unacknowledged work so one worker is not flooded.
        # TODO 3: Register a consumer with automatic acknowledgement disabled.
        # TODO 4: Validate/process the JSON, then acknowledge on this channel.
        # TODO 5: Print the message ID and RabbitMQ's redelivery flag.
        raise NotImplementedError(
            "Complete the manual-ack consumer without opening reference/."
        )
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
