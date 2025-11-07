import pika
import json
import os
from typing import List


class RabbitMQPublisher:
    """Publisher for sending job post IDs to RabbitMQ."""

    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.queue_name = os.getenv('RABBITMQ_QUEUE', 'job_posts_queue')
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection to RabbitMQ."""
        credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', 'guest'),
            os.getenv('RABBITMQ_PASSWORD', 'guest')
        )
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare queue (idempotent operation)
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        print(f"Connected to RabbitMQ at {self.host}:{self.port}")

    def publish_job_ids(self, job_ids: List[int]):
        """
        Publish list of job post IDs to the queue.

        Args:
            job_ids: List of database row IDs to process
        """
        if not self.channel:
            self.connect()

        for job_id in job_ids:
            message = json.dumps({'job_id': job_id})
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            print(f"Published job_id {job_id} to queue")

    def close(self):
        """Close connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("RabbitMQ connection closed")
