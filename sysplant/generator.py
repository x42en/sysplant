# -*- coding:utf-8 -*-

from typing import Union

from sysplant.utils.loggerSingleton import LoggerSingleton
from sysplant.managers.templateManager import TemplateManager


class Generator:
    """
    Main Class defining the generation algorithm. Nothing should be done to the data in here.
    Check TemplateManager (self.__engine) for data generation and modifications.
    """

    def __init__(
        self, arch: str = "x64", syscall: str = "syscall", language: str = "nim"
    ) -> None:
        """
        Init method.
        Will instanciate self.__engine private var used for template modifications

        Args:
            arch (str, optional): Code architecture to generate. Defaults to "x64".
            syscall (str, optional): Syscall instruction to used. Defaults to "syscall".
            language (str, optional): Language type for code generate. Defaults to "nim".
        """
        # Init default vars
        self.logger = LoggerSingleton()
        self.__engine = TemplateManager(arch, syscall, language)

        # Init language
        self.__language = language

    def generate(
        self, iterator: str, resolver: str, stub: str, syscalls: Union[str, list]
    ) -> str:
        """
        Public method defining the generation algorithm. This method does not touch any code directly.
        It should only call TemplateManager methods in specific order.
        Modifications are let to TemplateManager class.

        Args:
            iterator (str): Iterator name to use
            resolver (str): Resolver name to use
            stub (str): Stub type name to use
            syscalls (Union[str, list]): NtFunctions list names to hook, or preset name (all|common|donut)

        Raises:
            ValueError: _description_

        Returns:
            str: Template content after generation
        """
        self.logger.info("Summary of params used")
        self.logger.debug(
            "\t. NOTE: DEBUG Interruption set in caller stub !", stripped=True
        )
        self.logger.info(f"\t. Language: {self.__language.upper()}", stripped=True)

        # Set debug flag
        self.__engine.set_debug()

        # Generate random seed
        self.__engine.set_seed()

        # Set iterator
        self.logger.info(f"\t. Selected syscall iterator: {iterator}", stripped=True)
        self.__engine.set_iterator(iterator)

        # Set resolver
        self.logger.info(f"\t. Selected syscall resolver: {resolver}", stripped=True)
        self.__engine.set_resolver(resolver)

        # Generate caller
        self.logger.info(f"\t. Selected syscall caller stub: {stub}", stripped=True)
        self.__engine.set_caller(stub, resolver)

        # Generate stubs
        if syscalls == "all":
            self.logger.info("\t. All supported functions selected", stripped=True)
            syscalls = self.__engine.list_supported_syscalls()
        elif syscalls == "common":
            self.logger.info("\t. Common supported functions selected", stripped=True)
            syscalls = self.__engine.list_common_syscalls()
        elif syscalls == "donut":
            self.logger.info("\t. Donut functions selected", stripped=True)
            syscalls = self.__engine.list_donut_syscalls()
        elif type(syscalls) is not list:
            raise ValueError("Unsupported functions type")
        else:
            self.logger.info("\t. Custom set of functions selected", stripped=True)
        self.__engine.generate_stubs(syscalls)

        return str(self.__engine)

    def scramble(self, scramble: bool) -> str:
        """
        Public method used to randomize internal function names.
        Note: The concept behind this method is to let another project randomize the NtFunctions names as Sysplant as no view of the code using it.

        Args:
            scramble (bool): Randomize flag value

        Returns:
            str: Template content after modification
        """
        # If internal name randomization is required
        self.logger.info(f"\t. Randomize internal function: {scramble}", stripped=True)
        if scramble:
            self.__engine.scramble()

        return str(self.__engine)

    def output(self, output_path: str) -> str:
        """
        Public method used to write generated code to filename

        Args:
            output_path (str): Filename where to write generated code

        Returns:
            str: Template content
        """
        # Write file
        clean_path = (
            output_path
            if output_path.endswith(f".{self.__language}")
            else f"{output_path}.{self.__language}"
        )
        with open(clean_path, "w") as o:
            o.write(str(self.__engine))
            self.logger.info(f"Syscall file written to {clean_path}")

        return str(self.__engine)
