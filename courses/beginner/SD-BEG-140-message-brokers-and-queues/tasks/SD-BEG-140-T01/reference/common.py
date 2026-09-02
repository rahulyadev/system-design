"""Shared connection and topology contract for the reference implementation."""

from __future__ import annotations

import os

import pika


HOST = os.environ.get("SD_BEG_140_RABBITMQ_HOST", "127.0.0.1")
PORT = int(os.environ.get("SD_BEG_140_RABBITMQ_PORT", "5678"))
VHOST = "sd_beg_140"
USERNAME = "learner"
PASSWORD = "local-only-demo"
QUEUE_NAME = "sd_beg_140_tasks"


def connection_parameters() -> pika.ConnectionParameters:
    return pika.ConnectionParameters(
        host=HOST,
        port=PORT,
        virtual_host=VHOST,
        credentials=pika.PlainCredentials(USERNAME, PASSWORD),
        heartbeat=30,
        blocked_connection_timeout=30,
        connection_attempts=5,
        retry_delay=1,
    )


def open_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(connection_parameters())


def declare_queue(channel: pika.channel.Channel) -> None:
    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
        arguments={"x-queue-type": "quorum"},
    )
