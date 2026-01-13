import os
from redis import Redis
from loguru import logger

class ConnectionRedys:
    def __init__(self, host: str, port: int, db: int, **kwargs) -> None:
        logger.info(f"START CREATE REDIS CONNECTIONS :: HOST [ {host} ] | PORT [ {port} ] | DB [ {db} ]")
        self.client: Redis = Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            **kwargs
        )
        ...

