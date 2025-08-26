from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from src.config.database import engine, Base
import logging
import threading
import time

from src.services.rabbitmq.connection import rabbitmq_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_rabbitmq_consumers():
    """Setup RabbitMQ consumers (run in background thread)"""

    def email_callback(message, routing_key):
        logger.info(f"Processing email: {routing_key} - {message}")

    def sms_callback(message, routing_key):
        logger.info(f"Processing SMS: {routing_key} - {message}")

    def push_callback(message, routing_key):
        logger.info(f"Processing push: {routing_key} - {message}")

    callbacks = {
        'critical_email_queue': email_callback,
        'noncritical_email_queue': email_callback,
        'critical_sms_queue': sms_callback,
        'noncritical_sms_queue': sms_callback,
        'critical_push_queue': push_callback,
        'noncritical_push_queue': push_callback,
    }

    return callbacks


def start_rabbitmq_consumers():
    """Start RabbitMQ consumers in a background thread"""

    def consumer_worker():
        while True:
            try:
                if rabbitmq_connection.setup_infrastructure():
                    callbacks = setup_rabbitmq_consumers()
                    rabbitmq_connection.start_all_consumers(callbacks)
                else:
                    logger.error("Failed to setup RabbitMQ infrastructure, retrying in 10 seconds...")
                    time.sleep(10)
            except Exception as e:
                logger.error(f"RabbitMQ consumer error: {e}, restarting in 10 seconds...")
                time.sleep(10)

    consumer_thread = threading.Thread(target=consumer_worker, daemon=True)
    consumer_thread.start()
    return consumer_thread