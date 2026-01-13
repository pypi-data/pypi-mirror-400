import pika
import json
from loguru import logger

class RabbitMQConnection:
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        port: str,
        virtual_host: str,
        queue: str,
        routing_key: str,
        exchange: str
    ):
        self.queue: str = queue
        self.routing_key: str = routing_key
        self.exchange: str = exchange

        self.credential = pika.PlainCredentials(
            username=username,
            password=password
        )

        parameter = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=self.credential
        )

        connection = pika.BlockingConnection(parameter)
        self.channel = connection.channel()

        self.exchange = exchange
        self.routing_key = routing_key

    def close(self):
        if self.connection:
            self.connection.close()
