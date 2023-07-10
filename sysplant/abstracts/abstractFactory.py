# -*- coding:utf-8 -*-

import string
import random
import hashlib
import logging

from typing import Union

from abc import ABC
from sysplant.utils.loggerSingleton import LoggerSingleton
from sysplant.constants.sysplantConstants import SysPlantConstants


class AbstractFactory(ABC):
    """Public factory class handling standard methods used by child instances"""

    def __init__(self, log_level: int = logging.INFO) -> None:
        super().__init__()

        self.data: str = ""

        # Share logger for all childs
        self.logger = LoggerSingleton(log_level)

    def replace_tag(self, name: str, content: str) -> None:
        """Public method used to replace a TAG pattern in data var with content

        Args:
            name (str): the tag name to replace
            content (str): the content value to replace tag with
        """
        self.__replace_pattern(name, content)

    def __replace_pattern(
        self, pattern: str, content: Union[str, int], count: int = -1
    ) -> None:
        # Replace tag with content in template data
        self.data = self.data.replace(
            f"{SysPlantConstants.TAG_START}{pattern}{SysPlantConstants.TAG_END}",
            str(content),
            count,
        )

    def generate_random_seed(self) -> int:
        """Public method used to generate a random int used as seed
        Range from: 2^28 to (2^32 - 1)

        Returns:
            int: The generated random seed
        """
        return random.randrange(2**28, 2**32)

    def generate_random_string(
        self, length: int, choices: list = string.ascii_letters
    ) -> str:
        """Private method used to generate a random string

        Args:
            length (int): The random string length to generate
            choices (list, optional): The chars sapce to used for generation. Defaults to string.ascii_letters.

        Returns:
            str: The generated random string
        """
        return "".join(random.choice(choices) for _ in range(length))

    def get_function_hash(self, seed: int, name: str) -> int:
        """Public method used to hash kernel call to evade with random hex number in order to avoid static analysis detection.

        Args:
            name (str): The kernel call to evade

        Returns:
            int: The kernel call hashed
        """
        hash_value = hashlib.md5(f"{seed}{name[2:]}".encode())
        return int(hash_value.hexdigest()[:8], 16)
