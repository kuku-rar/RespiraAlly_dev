import pika
import os
import json

class RabbitMQService:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None

    def connect(self):
        """Establishes a connection and a channel."""
        if not self.connection or self.connection.is_closed:
            params = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            print("RabbitMQ connection established.")

    def publish_message(self, queue_name: str, message_body: dict):
        """Publishes a message to the specified queue."""
        try:
            self.connect()
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            message = json.dumps(message_body, ensure_ascii=False)
            
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
            print(f" [x] Sent {message} to queue '{queue_name}'")
        except Exception as e:
            print(f"Error publishing message: {e}")
            # In a real app, you might want to handle reconnection logic here
            raise
        finally:
            self.close()

    def close(self):
        """Closes the connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("RabbitMQ connection closed.")

# Create a singleton instance
rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
rabbitmq_service = RabbitMQService(rabbitmq_url)

def get_rabbitmq_service() -> RabbitMQService:
    """Dependency injector for RabbitMQService."""
    # In a real app, you might want more sophisticated connection management
    return rabbitmq_service
