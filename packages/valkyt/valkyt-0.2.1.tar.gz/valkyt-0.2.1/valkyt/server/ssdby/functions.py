from .connection import ConnectionSsdby
from loguru import logger
from valkyt.utils import Stream, File

class Ssdby(ConnectionSsdby):
    def __init__(self, host, port, **kwargs):
        super().__init__(host, port, **kwargs)
        
    def already_in_ssdb(self, tube: str, id: str, only_check: bool = False) -> bool:
        exist = self.client.hexists("{}".format(tube), "{}".format(id))
        if not exist:
            if not only_check:
                logger.info(f'[+] NEW ITEM ADD TO SSDB :: ITEM [ {id} ]')
                hset = self.client.hset(
                    "{}".format(tube), "{}".format(id), "{}".format(1)
                )
                if hset:
                    return False
            else:
                logger.info(f"ONLY CHECK ITEM NOT FOUND IN SSDB")
                return False
        else:
            logger.info(f'ITEM ALREDY IN SSDB :: ITEM [ {id} ]')
            return True
        ...
        
    def close(self) -> None:
        self.client.close()