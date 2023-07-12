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
        self.type_defined = set()

    @abstractmethod
    def generate_struct(self, name: str, definition: list) -> str:
        raise NotImplementedError("Structure generation not implemented yet")

    @abstractmethod
    def generate_union(self, name: str, definition: list) -> str:
        raise NotImplementedError("Union generation not implemented yet")

    @abstractmethod
    def generate_pointer(self, name: str, definition: list) -> str:
        raise NotImplementedError("Pointer generation not implemented yet")

    @abstractmethod
    def generate_standard(self, name: str, definition: list) -> str:
        raise NotImplementedError("Standard var generation not implemented yet")

    @abstractmethod
    def generate_enum(self, name: str, definition: list) -> str:
        raise NotImplementedError("Enum generation not implemented yet")

    @abstractmethod
    def generate_seed(self, name: str, definition: list) -> str:
        raise NotImplementedError("Seed generation not implemented yet")

    @abstractmethod
    def generate_stub(self, name: str, params: dict, fhash: int) -> str:
        raise NotImplementedError("Stub generation not implemented yet")

    @abstractmethod
    def generate_definitions(self) -> str:
        raise NotImplementedError("Type definition generation not implemented yet")
