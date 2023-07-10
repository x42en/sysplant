# -*- coding:utf-8 -*-

import logging

from abc import ABC, abstractmethod
from sysplant.utils.loggerSingleton import LoggerSingleton


class AbstractGenerator(ABC):
    """
    Public generator class handling standard methods used by child instances
    """

    def __init__(self, log_level: int = logging.INFO) -> None:
        super().__init__()

        # Share logger for all childs
        self.logger = LoggerSingleton(log_level)

        # Store definitions already defined
        self.defined = set()

    @abstractmethod
    def generate_struct(self, name: str, definition: list) -> str:
        raise NotImplementedError("Not implemented yet")

    @abstractmethod
    def generate_union(self, name: str, definition: list) -> str:
        raise NotImplementedError("Not implemented yet")

    @abstractmethod
    def generate_pointer(self, name: str, definition: list) -> str:
        raise NotImplementedError("Not implemented yet")

    @abstractmethod
    def generate_standard(self, name: str, definition: list) -> str:
        raise NotImplementedError("Not implemented yet")

    @abstractmethod
    def generate_enum(self, name: str, definition: list) -> str:
        raise NotImplementedError("Not implemented yet")

    @abstractmethod
    def generate_seed(self, name: str, definition: list) -> str:
        raise NotImplementedError("Not implemented yet")

    @abstractmethod
    def generate_header(self, name: str, definition: list) -> str:
        raise NotImplementedError("Not implemented yet")
