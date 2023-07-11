# -*- coding:utf-8 -*-

from typing import Union

from sysplant.abstracts.abstractFactory import AbstractFactory
from sysplant.managers.templateManager import TemplateManager
from sysplant.constants.sysplantConstants import SysPlantConstants


class Generator(AbstractFactory):
    """
    Main Class used to generate and manipulate Nim code
    """

    def __init__(self, syscall: str = "syscall", language: str = "nim") -> None:
        super().__init__()
        self.__engine = TemplateManager(language)

        if syscall not in ["syscall", "int 0x2e"]:
            raise NotImplementedError("Unsupported syscall instruction")

        # Load base template
        self.__engine.load_base()

        # Init syscall instruction
        self.__instruction = syscall

        # Init language
        self.__language = language

    def generate(
        self,
        iterator: str,
        resolver: str,
        stub: str,
        syscalls: Union[str, list],
        scramble: bool,
        output: str,
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

        # Generate stubs
        self.logger.info(f"\t. Selected syscall stub: {stub}", stripped=True)
        syscall_stub = TemplateManager(self.__language)

        # Resolve all headers for functions to hook
        entries = self.__engine.select_functions(syscalls)
        stubs_code = ""

        # Loop functions to hook
        for name, params in entries.items():
            # Reset stub
            syscall_stub.load_stub(stub)

            # Generate function declaration
            syscall_stub.generate_header(name, params)

            # Replace resolver functions in stub
            func_resolver = (
                "SPT_GetRandomSyscallAddress"
                if resolver == "random"
                else "SPT_GetSyscallAddress"
            )
            syscall_stub.replace_tag("FUNCTION_RESOLVE", func_resolver)

            # Calculate function hash
            hash_value = self.get_function_hash(seed, name)
            syscall_stub.replace_tag("FUNCTION_HASH", hex(hash_value))

            # Replace syscall instruction if set in template
            syscall_stub.replace_tag("SYSCALL_INST", self.__instruction)

            # Append stub
            stubs_code += str(syscall_stub) + "\n\n"

        # Replace syscall stubs
        self.__engine.replace_tag("SYSCALL_STUBS", stubs_code)

        # Resolve required type definition
        self.__engine.generate_definitions(syscall_stub.get_definitions())

        # If internal name randomization is required
        self.logger.info(f"\t. Randomize internal function: {scramble}", stripped=True)
        if scramble:
            self.__engine.scramble()

        # Write file
        output_path = output if output.endswith(".nim") else f"{output}.nim"
        with open(output_path, "w") as o:
            o.write(str(self.__engine))
        self.logger.info(f"Syscall file written to {output_path}")

        return str(self.__engine)
