# -*- coding:utf-8 -*-

from typing import Union

from sysplant.abstracts.abstractFactory import AbstractFactory
from sysplant.managers.templateManager import TemplateManager
from sysplant.constants.sysplantConstants import SysPlantConstants


class Generator(AbstractFactory):
    """
    Main Class used to generate and manipulate Nim code
    """

    def __init__(
        self, arch: str = "x64", syscall: str = "syscall", language: str = "nim"
    ) -> None:
        super().__init__()
        self.__engine = TemplateManager(arch, language, syscall)

        if syscall not in ["syscall", "int 0x2e"]:
            raise NotImplementedError("Unsupported syscall instruction")

        # Load base template
        self.__engine.load_base()

        # Init language
        self.__language = language

    def generate(
        self, iterator: str, resolver: str, stub: str, syscalls: Union[str, list]
    ) -> str:
        self.logger.info("Summary of params used")
        self.logger.info(f"\t. Language: {self.__language.upper()}", stripped=True)

        # Set debug flag
        self.__engine.set_debug()

        # Generate random seed
        seed = self.__engine.set_seed()

        # Set iterator
        self.logger.info(f"\t. Selected syscall iterator: {iterator}", stripped=True)
        self.__engine.set_iterator(iterator)

        # Set resolver
        self.logger.info(f"\t. Selected syscall resolver: {resolver}", stripped=True)
        self.__engine.set_resolver(resolver)

        # Generate caller stub
        self.logger.info(f"\t. Selected syscall caller stub: {stub}", stripped=True)
        self.__engine.set_caller(stub, resolver)

        # Resolve all headers for functions to hook
        entries = self.__engine.select_functions(syscalls)
        stubs_code = ""

        # Loop functions to hook
        for name, params in entries.items():
            # Calculate function hash
            hash_value = self.get_function_hash(seed, name)

            # Generate stub
            stubs_code += self.__engine.generate_stub(name, params, hash_value)

        # Replace syscall stubs
        self.__engine.replace_tag("SPT_STUBS", stubs_code)

        # Resolve required type definition
        self.__engine.generate_definitions()

    def scramble(self, scramble: bool) -> None:
        # If internal name randomization is required
        self.logger.info(f"\t. Randomize internal function: {scramble}", stripped=True)
        if scramble:
            self.__engine.scramble()

    def output(self, output_path: str) -> str:
        # Write file
        clean_path = (
            output_path if output_path.endswith(".nim") else f"{output_path}.nim"
        )
        with open(clean_path, "w") as o:
            o.write(str(self.__engine))
        self.logger.info(f"Syscall file written to {clean_path}")

        return str(self.__engine)
