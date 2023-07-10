# -*- coding:utf-8 -*-

import random
import hashlib
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

        # Init seed
        self.__seed = 0

        # Init syscall instruction
        self.__instruction = syscall

        # Init language
        self.__language = language

        self.__defined = set()

    def __str__(self) -> str:
        return str(self.__engine)

    def __generate_random_seed(self) -> int:
        """Public method used to generate a random int used as seed
        Range from: 2^28 to (2^32 - 1)

        Returns:
            int: The generated random seed
        """
        return random.randrange(2**28, 2**32)

    def __get_function_hash(self, name: str) -> int:
        """Private method used to hash kernel call to evade with random hex number in order to avoid static analysis detection.

        Args:
            name (str): The kernel call to evade

        Returns:
            int: The kernel call hashed
        """
        hash_value = hashlib.md5(f"{self.__seed}{name[2:]}".encode())
        return int(hash_value.hexdigest()[:8], 16)

    def set_seed(self, seed: int = 0) -> str:
        if seed <= 0:
            # Generate seed
            self.__seed = self.__generate_random_seed()
        else:
            self.__seed = seed
        return self.__engine.set_seed(self.__seed)

    def set_iterator(self, name: str) -> str:
        return self.__engine.set_iterator(name)

    def set_resolver(self, name: str) -> str:
        return self.__engine.set_resolver(name)

    def __generate_header(self, name: str, params: dict) -> str:
        # Generate function header
        header = f"proc {name}*("
        # Build function param declaration
        args = list()
        for p in params.get("params", []):
            # Register each type var
            self.__defined.add(p["type"])
            args.append(f"{p['name']}: {p['type']}")
        header += ", ".join(args)
        header += ") {.asmNoStackFrame.} ="
        return header

    def generate(
        self,
        iterator: str,
        resolver: str,
        stub: str,
        syscalls: Union[str, list],
        output: str,
    ) -> str:
        self.logger.info("Summary of params used")
        self.logger.info(f"\t. Language: {self.__language.upper()}", stripped=True)

        self.set_seed()

        # Set iterator
        self.logger.info(f"\t. Selected syscall iterator: {iterator}", stripped=True)
        self.set_iterator(iterator)

        # Set resolver
        self.logger.info(f"\t. Selected syscall resolver: {resolver}", stripped=True)
        self.set_resolver(resolver)

        # Resolve all headers for functions to hook
        entries = self.__engine.select_prototypes(syscalls)

        # Generate stubs
        self.logger.info(f"\t. Selected syscall stub: {stub}", stripped=True)
        syscall_stub = TemplateManager(self.__language)
        stubs_code = ""

        # Loop functions to hook
        for name, params in entries.items():
            # Reset stub
            syscall_stub.load_stub(stub)

            # Generate function declaration
            header = self.__generate_header(name, params)
            syscall_stub.replace_tag("PROC_DEFINITION", header)

            # Replace resolver functions in stub
            func_resolver = (
                "SPT_GetRandomSyscallAddress"
                if resolver == "random"
                else "SPT_GetSyscallAddress"
            )
            syscall_stub.replace_tag("FUNCTION_RESOLVE", func_resolver)

            # Calculate function hash
            hash_value = self.__get_function_hash(name)
            syscall_stub.replace_tag("FUNCTION_HASH", hex(hash_value))

            # Replace syscall instruction if set in template
            syscall_stub.replace_tag("SYSCALL_INST", self.__instruction)

            # Append stub
            stubs_code += str(syscall_stub) + "\n\n"

        # Replace syscall stub
        self.__engine.replace_tag("SYSCALL_STUBS", stubs_code)

        # Resolve required type definition
        self.__engine.generate_definitions(self.__defined)

        # Write file
        output_path = output if output.endswith(".nim") else f"{output}.nim"
        with open(output_path, "w") as o:
            o.write(str(self.__engine))
        self.logger.info(f"Syscall file written to {output_path}")

        return str(self.__engine)
