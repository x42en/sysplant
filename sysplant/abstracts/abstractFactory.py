# -*- coding:utf-8 -*-

import logging

from abc import ABC
from sysplant.utils.loggerSingleton import LoggerSingleton


class AbstractFactory(ABC):
    """Public factory class handling standard methods used by child instances"""

    def __init__(self, log_level: int = logging.INFO) -> None:
        super().__init__()

        # Share logger for all childs
        self.logger = LoggerSingleton(log_level)
