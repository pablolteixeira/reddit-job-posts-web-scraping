"""
RabbitMQ consumer that processes job posts from the queue.
"""
import os
import json
import time
import pika
from dotenv import load_dotenv
from database import DatabaseClient
from analyzer import clean_and_extract_text

load_dotenv()


class JobPostConsumer:
    """Consumer for processing job posts from RabbitMQ queue."""

    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.queue_name = os.getenv('RABBITMQ_QUEUE', 'job_posts_queue')
        self.connection = None
        self.channel = None
        self.db_client = DatabaseClient()

    def connect(self):
        """Connect to RabbitMQ with retry logic."""
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(
                    os.getenv('RABBITMQ_USER', 'guest'),
                    os.getenv('RABBITMQ_PASSWORD', 'guest')
                )
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name, durable=True)

                # Set QoS to process one message at a time
                self.channel.basic_qos(prefetch_count=1)

                print(f"Connected to RabbitMQ at {self.host}:{self.port}")
                return True

            except Exception as e:
                print(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Failed to connect to RabbitMQ after all retries")
                    raise

    def process_message(self, ch, method, properties, body):
        """
        Process a single job post message from the queue.

        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        try:
            # Parse message
            message = json.loads(body)
            job_id = message.get('job_id')

            if not job_id:
                print(f"Invalid message format: {message}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            print(f"Processing job ID: {job_id}")

            # Fetch job post from database
            job_post = self.db_client.fetch_job_post(job_id)
            if not job_post:
                print(f"Job post {job_id} not found in database")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Check if already processed
            if job_post.processed_at:
                print(f"Job post {job_id} already processed, skipping...")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Analyze job post with LLM
            print(f"Analyzing job post {job_id} with Ollama...")
            cleaned_title, cleaned_text, tags = clean_and_extract_text(
                job_post.title,
                job_post.body or ""
            )

            # Update database with cleaned data
            success = self.db_client.update_cleaned_data(
                job_id=job_id,
                cleaned_title=cleaned_title,
                cleaned_text=cleaned_text,
                tags=tags
            )

            if success:
                print(f"Successfully processed job ID: {job_id}")
                print(f"  Title: {cleaned_title[:50]}...")
                print(f"  Tags: {tags}")
            else:
                print(f"Failed to update database for job ID: {job_id}")

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError as e:
            print(f"Failed to parse message: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing message: {e}")
            # Don't acknowledge - message will be requeued
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from the queue."""
        print(f"Starting consumer on queue: {self.queue_name}")
        print("Waiting for messages. To exit press CTRL+C")

        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.process_message,
            auto_ack=False
        )

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\nShutting down consumer...")
            self.stop()

    def stop(self):
        """Stop consuming and close connections."""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        self.db_client.close()
        print("Consumer stopped")


def main():
    """Main entry point for the consumer."""
    consumer = JobPostConsumer()

    try:
        consumer.connect()
        consumer.start_consuming()
    except Exception as e:
        print(f"Fatal error: {e}")
        consumer.stop()


if __name__ == "__main__":
    main()
