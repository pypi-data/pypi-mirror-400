import os
import json

from kafka import KafkaProducer

class ConnectionKafka:
    def __init__(self, bootstraps: list) -> KafkaProducer:
        self.client = KafkaProducer(bootstrap_servers=bootstraps)
        ...
