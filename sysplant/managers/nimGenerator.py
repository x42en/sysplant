# -*- coding:utf-8 -*-

import json

import importlib.resources as pkg_resources

from sysplant import data as pkg_data

from sysplant.abstracts.abstractGenerator import AbstractGenerator
from sysplant.constants.sysplantConstants import SysPlantConstants


class NIMGenerator(AbstractGenerator):
    """
    Main class responsible for NIM code generation
    """

    def __init__(self) -> None:
        super().__init__()

        try:
            # load the winim library file responsible for type definition. This prevent duplicate definitions.
            # This file might be updated regularly until all the types are integrated inside Winim library (PR to do)
            self.set_extra_definitions("windef.nim")
        except Exception as err:
            raise SystemError(f"Unable to load mandatory data in NIM Generator: {err}")

    def generate_struct(self, name: str, definition: list) -> str:
        """
        Public method used to generate a NIM basic structure.
        The structure will be generated as a public object for external code usages.
        A pointer to the structure will always be generated in the form of: P+NAME

        Args:
            name (str): Structure name
            definition (list): Structure parameters from definitions.json

        Returns:
            str: NIM code for basic structure definition (except type keyword for definition chaining)
        """
        result = f"{SysPlantConstants.NIM_TAB}{name}* " + "{.pure.} = object\n"
        for var in definition:
            if len(var) == 2:
                result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]}: {var[0]}\n"

            elif len(var) == 3:
                result += (
                    f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]} "
                    + "{.bitsize: "
                    + str(var[2])
                    + ".}: "
                    + f"{var[0]}\n"
                )
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name}* = ptr {name}\n"

        return result

    def generate_union(self, name: str, definition: list) -> str:
        """
        Public method used to generate NIM union structure when a parent needs it.
        This structure will be generated as a private object as it won't be directly accessed by external code.
        A pointer to the union structure will always be generated in the form of: P+NAME

        Args:
            name (str): Union structure name
            definition (list): Union structure parameters from definitions.json

        Returns:
            str: NIM code for union structure definition (except type keyword for definition chaining)
        """
        result = f"{SysPlantConstants.NIM_TAB}{name} " + "{.pure, union.} = object\n"
        for var in definition:
            if len(var) == 2:
                result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]}: {var[0]}\n"
            elif len(var) == 3:
                result += (
                    f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]} "
                    + "{.bitsize: "
                    + var[2]
                    + ".}: "
                    + f"{var[0]}\n"
                )
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name} = ptr {name}\n"

        return result

    def generate_pointer(self, name: str, definition: list) -> str:
        """
        Public method used to generate NIM pointer to defined var
        The pointer will be geneerated as a public object for external code usages.

        Args:
            name (str): Pointer name
            definition (list): Type definition to point to from definitions.json

        Returns:
            str: NIM code for standard pointer declaration
        """
        result = f"{SysPlantConstants.NIM_TAB}{name}* = ptr {definition[0]}\n"
        return result

    def generate_standard(self, name: str, definition: list) -> str:
        """
        Public method used to generate NIM varaiable declaration.
        The variable will be generated as a public object for external code usages.
        A pointer to the variable will always be generated in the form of: P+NAME

        Args:
            name (str): Variable name
            definition (list): Variable type from definitions.json

        Returns:
            str: NIM code for variable definition (except type keyword for definition chaining)
        """
        result = f"{SysPlantConstants.NIM_TAB}{name}* = {definition[0]}\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name}* = ptr {name}\n"
        return result

    def generate_enum(self, name: str, definition: list) -> str:
        """
        Public method used to generate NIM enum declaration.
        The enum structure will be generated as a public object for external code usages.
        A pointer to the enum structure will always be generated in the form of: P+NAME

        Args:
            name (str): Enum structure name
            definition (list): Enum structure entries from definitions.json

        Returns:
            str: NIM code for enum structure (except type keyword for definition chaining)
        """
        result = f"{SysPlantConstants.NIM_TAB}{name}* " + "{.pure.} = enum\n"
        for var in definition:
            result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var},\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name}* = ptr {name}\n"

        return result

    def generate_debug(self, debug: bool) -> str:
        """
        Public method used to generate the SPT_DEBUG constant flag

        Args:
            debug (bool): Debug flag value

        Returns:
            str: NIM code for template integration
        """
        return f"const SPT_DEBUG = {str(debug).lower()}"

    def generate_seed(self, seed: int) -> str:
        """
        Public method used to generate the SPT_SEED constant value

        Args:
            seed (int): Seed value

        Returns:
            str: NIM code for template integration
        """
        return f"const SPT_SEED = {hex(seed)}"

    def generate_stub(self, name: str, params: dict, fhash: int) -> str:
        """
        Public method used to generate stub code of syscall to hook

        Args:
            name (str): NtFunction name to hook
            params (dict): Parameters of functions defined in prototypes.json
            fhash (int): NtFunction hash value used by ASM call

        Returns:
            str: NIM code for template integration
        """
        # Build function param declaration
        stub = f"proc {name}*("
        args = list()

        # Loop function params
        for p in params.get("params", []):
            # Register each type var
            self.type_set.add(p["type"])
            args.append(f"{p['name']}: {p['type']}")

        # Generate NIM proc parameters
        stub += ", ".join(args)
        stub += ") {.asmNoStackFrame.} =\n"

        # Append stub code
        stub += f'{SysPlantConstants.NIM_TAB}asm """\n'
        stub += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}push dword ptr {hex(fhash)}\n"
        stub += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}call `SPT_Syscall`\n"
        stub += f'{SysPlantConstants.NIM_TAB}"""\n'

        return stub
