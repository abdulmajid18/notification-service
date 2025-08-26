import json
import logging
from typing import List, Dict

import pika
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username, password)
        )
        self.connection = None
        self.channel = None
        self.exchange_name = 'notification_exchange'
        self.exchange_type = 'direct'

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            logger.info("Connected to RabbitMQ successfully")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def setup_exchange(self):
        """Declare the direct exchange"""
        try:
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type=self.exchange_type,
                durable=True
            )
            logger.info(f"Exchange '{self.exchange_name}' declared as '{self.exchange_type}'")
        except Exception as e:
            logger.error(f"Failed to declare exchange: {e}")
            raise

    def create_queue(self, queue_name: str, routing_keys: List[str]):
        """Create a queue and bind it to the exchange with routing keys"""
        try:
            # Declare queue
            self.channel.queue_declare(queue=queue_name, durable=True)

            # Bind queue to exchange with each routing key
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

    def start_consumer(self, queue_name: str, callback):
        """Start a consumer for a specific queue"""

        def wrapped_callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode())
                callback(message, method.routing_key)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapped_callback,
            auto_ack=False
        )

    def start_all_consumers(self, callbacks: Dict[str, callable]):
        """Start consumers for all queues"""
        for queue_name, callback in callbacks.items():
            self.start_consumer(queue_name, callback)

        logger.info("Starting consumers...")
        self.channel.start_consuming()

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Connection closed")