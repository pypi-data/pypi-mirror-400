import json

from typing import Generator, Dict
from loguru import logger

from .connection import ConnectionBeanstalk, TimedOutError, Client, Job

class Beanstalk:
    def __init__(self, host: str, port: str, tube: str) -> None:
        self.connection: ConnectionBeanstalk = ConnectionBeanstalk(host, port, tube)
        self.job: Job = None
        ...
        
    def get(self) -> Generator[Dict[str, any], any, None]:
        while True:
            try:
                self.job = self.connection.client.reserve(timeout=10)
                yield json.loads(self.job.body)
                self.__delete()
            except TimedOutError:
                yield None
            except BrokenPipeError:
                raise
            except Exception:
                raise
            
    def put(self, output: str, **kwargs) -> None:
        self.connection.client.put(body=output, **kwargs)
        ...

    def __delete(self):
        if self.job:
            try:
                self.connection.client.delete(self.job)
                self.job = None
            except Exception as err:
                logger.warning(f'BEANSTALK DELETED :: MESSAGE [ {str(err)} ]')

    def __bury(self, **kwargs) -> None:
        if self.job:
            try:
                self.connection.client.bury(self.job, **kwargs)
                self.job = None
            except Exception as err:
                logger.warning(f'BEANSTALK BURRY :: MESSAGE [ {str(err)} ]')
        ...

    def exception_handler(self, **kwargs) -> None:
        try:
            action = kwargs.get("action")
            if action == "delete":
                self.__delete()
            else:
                self.__bury()
        except Exception as err:
            logger.error(f"EXCEPTION HANDLER ERROR :: MESSAGE [ {str(err)} ]")
