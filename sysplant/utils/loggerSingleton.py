# -*- coding:utf-8 -*-

import logging

from sysplant.utils.singleton import Singleton


class LoggerSingleton(metaclass=Singleton):
    """Simple class used to display messages on CLI.
    Using as a singleton so it will share the log_level everywhere

    Args:
        metaclass (_type_, optional): _description_. Defaults to Singleton.
    """

    def __init__(self, log_level: int = logging.INFO) -> None:
        self.log_level = log_level

    def __output(self, message: str, level: int) -> None:
        """Private method used to output colorized message if log_level is match

        Args:
            message (str): the message to output
            level (int): the message level, will be compared to configured log_level

        """
        if level >= self.log_level:
            print(f"{message}")

    def isDebug(self) -> bool:
        """Public method used to detect debug conditions

        Returns:
            bool: debug state
        """
        return self.log_level == logging.DEBUG

    def debug(self, message: str, stripped: bool = False) -> None:
        """Public method used to display debug message (Default: cyan and starting with '[*] ')

        Args:
            message (str): the debug message to output
            stripped (bool, optional): strip the starting pattern '[*] '. Defaults to False.
        """
        start = "[*] " if not stripped else ""
        self.__output(f"{start}{message}", logging.DEBUG)

    def info(self, message: str, stripped: bool = False) -> None:
        """Public method used to display info message (Default: green and starting with '[+] ')

        Args:
            message (str): the info message to output
            stripped (bool, optional): strip the starting pattern '[+] '. Defaults to False.
        """
        start = "[+] " if not stripped else ""
        self.__output(f"{start}{message}", logging.INFO)

    def warning(self, message: str, stripped: bool = False) -> None:
        """Public method used to display warning message (Default: yellow and starting with '[!] ')

        Args:
            message (str): the warning message to output
            stripped (bool, optional): strip the starting pattern '[!] '. Defaults to False.
        """
        start = "[.] " if not stripped else ""
        self.__output(f"{start}{message}", logging.WARNING)

    def error(self, message: str, stripped: bool = False) -> None:
        """Public method used to display error message (Default: red and starting with '[!] ')

        Args:
            message (str): the error message to output
            stripped (bool, optional): strip the starting pattern '[!] '. Defaults to False.
        """
        start = "[!] " if not stripped else ""
        self.__output(f"{start}{message}", logging.ERROR)

    def critical(self, message: str, stripped: bool = False) -> None:
        """Public method used to display critical message (Default: red and starting with '[!!] ')

        Args:
            message (str): the critical message to output
            stripped (bool, optional): strip the starting pattern '[!!] '. Defaults to False.
        """
        start = "[x] " if not stripped else ""
        self.__output(f"{start}{message}", logging.CRITICAL)

    def output(self, message: str) -> None:
        """Public method used to display raw message without conditions or color

        Args:
            message (str): mesasge to display
        """
        print(message)
