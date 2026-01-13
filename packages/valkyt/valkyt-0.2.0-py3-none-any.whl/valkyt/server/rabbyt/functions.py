import json
import pika

from loguru import logger
from .connection import RabbitMQConnection

class Rabbyt(RabbitMQConnection):
    def send(self, data: dict):
        body = json.dumps(data)
        self.channel\
            .basic_publish(exchange=self.exchange,routing_key=self.routing_key, body=body)
        logger.info(f"Message sent to RabbitMQ: {body}")


