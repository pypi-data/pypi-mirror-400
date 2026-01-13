
import json
import os

from loguru import logger

from .connection import ConnectionKafka
from valkyt.utils import Stream, File

class Kafkaa(ConnectionKafka):
    def __init__(self, bootstraps):
        super().__init__(bootstraps)
    
    
    def send(self, data: dict, topic: str, bootstrap: str) -> None:
        logs = self.client.send(topic=topic, value=str.encode(json.dumps(data))).get(timeout=10)
        logger.info(f'SEND KAFKA :: MESSAGE [ {logs} ]')
        Stream.shareKafka(topic)

    @staticmethod
    def local2kafka(source: str, topic: str, bootstrap: str) -> None:
        for root, _, files in os.walk(source.replace('\\', '/')):
            for file in files:
                if file.endswith('json'):
                    file_path = os.path.join(root, file).replace('\\', '/')
                    Stream.shareKafka(topic)
                    data: dict = File.read_json(file_path)
                    Kafkaa.send(data, topic, bootstrap)