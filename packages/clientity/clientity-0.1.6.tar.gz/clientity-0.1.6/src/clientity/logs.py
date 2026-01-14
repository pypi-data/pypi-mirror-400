from __future__ import annotations
import os, typing as t

from loguru import logger
from loguru._logger import Logger

class DevNull:
    def __init__(self) -> None:
       self.debug = self.__ignore
       self.info = self.__ignore
       self.warning = self.__ignore
       self.error = self.__ignore
       self.critical = self.__ignore

    def __ignore(self, *args, **kwargs) -> None: pass

def devlogs() -> bool:
    env = os.getenv('CLIENTITYLOGS', '').strip()
    if not env: return False
    return (env.lower() in ['1', 'true', 'yes', 't'])


devnull = DevNull()
log = logger if devlogs() else devnull

Log = t.Union[Logger, DevNull]
