import os
import json

from json import dumps

from typing import Any, Dict
from loguru import logger
from botocore.exceptions import ClientError
from .connection import ConnectionRedys

class Redys(ConnectionRedys):
    def __init__(self, host, port, db, **kwargs):
        super().__init__(host, port, db, **kwargs)
        
    def check(self, key: str, id: str, **kwargs) -> Dict:
        """
        Examples:
            >>> check(key="xxxx:xxxx:xxxx", id="xxxxxx")
            {
                "data": xxxxx
            }
            
            >>> check(key="xxxx:xxxx:xxxx", id="xxxxxx")
            None
        """
        __key: str = "{}:{}".format(
            key,
            id
        )
        __key = self.client.get(__key)
        if __key:
            logger.info(f'DATA ALREDY IN REDIS :: ID [ {id} ]')
            return json.loads(__key)
        return None
        ...
        
    def push(self, data: str, key: str, id: str, **kwargs):
        """
        Examples:
            >>> push(
                data={
                    "data": xxxxx
                },
                key="xxxx:xxxx:xxxx",
                id="xxxxxx"
            )
        """
        self.client.set(
            "{}:{}".format(
                key,
                id
            ),
            json.dumps(
                data,
                ensure_ascii=False
            ),
            **kwargs
        )
        logger.info(f"NEW DATA ADD IN REDIS :: ID [ {id} ]")