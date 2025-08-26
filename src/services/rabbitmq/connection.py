import json
import logging
import os
import time
from dataclasses import asdict
from typing import List, Dict, Optional, Callable

import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from src.schemas.notification import NotificationEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQConnection:
    _instance: Optional['RabbitMQConnection'] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        if hasattr(self, '_initialized'):
            return
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username, password),
            heartbeat=600,
            blocked_connection_timeout=300,
            retry_delay=5,
            connection_attempts=3
        )
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self.exchange_name = 'notification_exchange'
        self.exchange_type = 'direct'
        self._initialized = True
        self._consuming = False

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            if self.connection and self.connection.is_open:
                logger.info("RabbitMQ connection already established")
                return True

            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            logger.info("Connected to RabbitMQ successfully")
            return True

        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected connection error: {e}")
            return False

    def ensure_connection(self) -> bool:
        """Ensure we have a valid connection, reconnect if needed"""
        if not self.connection or self.connection.is_closed:
            return self.connect()
        return True

    def setup_infrastructure(self) -> bool:
        """Setup exchange and queues"""
        try:
            if not self.ensure_connection():
                return False

            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type=self.exchange_type,
                durable=True
            )
            logger.info(f"Exchange '{self.exchange_name}' declared")

            self.setup_queues()
            return True

        except AMQPChannelError as e:
            logger.error(f"Channel error during setup: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected setup error: {e}")
            return False

    def create_queue(self, queue_name: str, routing_keys: List[str]):
        """Create a queue and bind it to the exchange with routing keys"""
        try:
            if not self.ensure_connection():
                raise Exception("No RabbitMQ connection available")

            self.channel.queue_declare(queue=queue_name, durable=True)

            for routing_key in routing_keys:
                self.channel.queue_bind(
                    exchange=self.exchange_name,
                    queue=queue_name,
                    routing_key=routing_key
                )
                logger.info(f"Queue '{queue_name}' bound with routing key '{routing_key}'")

        except Exception as e:
            logger.error(f"Failed to create/bind queue {queue_name}: {e}")
            raise

    def setup_queues(self):
        """Setup all required queues with their bindings"""
        queue_bindings = {
            'critical_email_queue': ['critical.email'],
            'critical_sms_queue': ['critical.sms'],
            'critical_push_queue': ['critical.push'],
            'noncritical_email_queue': ['noncritical.email'],
            'noncritical_sms_queue': ['noncritical.sms'],
            'noncritical_push_queue': ['noncritical.push'],
        }

        for queue_name, routing_keys in queue_bindings.items():
            self.create_queue(queue_name, routing_keys)

    def start_consumer(self, queue_name: str, callback: Callable):
        """Start a consumer for a specific queue"""

        def wrapped_callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode())
                callback(message, method.routing_key)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        try:
            if not self.ensure_connection():
                raise Exception("No RabbitMQ connection available")

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=wrapped_callback,
                auto_ack=False
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start consumer for {queue_name}: {e}")
            return False

    def start_all_consumers(self, callbacks: Dict[str, Callable]):
        """Start consumers for all queues"""
        try:
            for queue_name, callback in callbacks.items():
                if not self.start_consumer(queue_name, callback):
                    raise Exception(f"Failed to start consumer for {queue_name}")

            logger.info("Starting consumers...")
            self._consuming = True
            self.channel.start_consuming()

        except Exception as e:
            logger.error(f"Failed to start consumers: {e}")
            self._consuming = False
            raise

    def stop_consuming(self):
        """Stop all consumers"""
        if self.channel and self._consuming:
            self.channel.stop_consuming()
            self._consuming = False
            logger.info("Stopped all consumers")

    def close(self):
        """Close the connection gracefully"""
        try:
            self.stop_consuming()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
        finally:
            self.connection = None
            self.channel = None

    def send_notification(self, event: NotificationEvent) -> bool:
        """Send a notification to the exchange"""
        try:
            if not self.ensure_connection():
                logger.error("Cannot send notification: No RabbitMQ connection")
                return False

            body = asdict(event)
            body["timestamp"] = time.time()

            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=event.routing_key,
                body=json.dumps(body),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )

            logger.info(f"Sent notification: {event.routing_key} - {event.message}")
            return True

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

rabbitmq_connection = RabbitMQConnection(
    host=os.getenv('RABBIT_HOST', 'rabbitmq'),
    port=5672,
    username=os.getenv('RABBIT_USER', 'guest'),
    password=os.getenv('RABBIT_PASSWORD', 'guest')
)
