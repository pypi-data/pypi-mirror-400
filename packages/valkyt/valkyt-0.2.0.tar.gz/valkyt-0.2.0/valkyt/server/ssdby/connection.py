import redis
from loguru import logger

class ConnectionSsdby:
    def __init__(self, host: str, port: int, **kwargs) -> None:
        logger.info(f"START CREATE SSDB CONNECTIONS :: HOST [ {host} ] | PORT [ {port} ]")
        self.client = redis.StrictRedis(
            host=host,
            port=port,
            **kwargs
        )
