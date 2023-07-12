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

        self.__definitions: dict = {}
        self.__winimdef = ""

        try:
            # Alaways load prototypes & typedefinitions
            self.__load_definitions()
            self.__load_winimdef()
        except Exception as err:
            raise SystemError(f"Unable to load mandatory data in NIM Generator: {err}")

    def __load_template(self, pkg_module: str, name: str) -> str:
        if name is None:
            raise ValueError("Template name can not be null")

        # Check only extension dot is set
        if not name.replace(".", "", 1).isalpha():
            raise ValueError("Invalid template name")

        # Adapt module based on what to load
        raw = pkg_resources.open_text(pkg_module, name)
        return raw.read()

    def __load_definitions(self) -> None:
        # Load supported functions definitions
        data = self.__load_template(pkg_data, "definitions.json")
        self.__definitions = json.loads(data)

    def __load_winimdef(self) -> None:
        # Load supported functions definitions
        self.__winimdef = self.__load_template(pkg_data, "windef.nim")

    def generate_struct(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name}* " + "{.pure.} = object\n"
        for var in definition:
            if len(var) >= 2:
                result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]}: {var[0]}\n"

            # I have not found how to initialize value in NIM type definitions...
            # elif len(var) == 3:
            #     result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]}: {var[0]} = {var[2]}\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name}* = ptr {name}\n"

        return result

    def generate_union(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name} " + "{.pure, union.} = object\n"
        for var in definition:
            if len(var) == 2:
                result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]}: {var[0]}\n"
            elif len(var) == 3:
                result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]}: {var[0]} = {var[2]}\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name} = ptr {name}\n"

        return result

    def generate_pointer(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name}* = ptr {definition[0]}\n"
        return result

    def generate_standard(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name}* = {definition[0]}\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name}* = ptr {name}\n"
        return result

    def generate_enum(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name}* " + "{.pure.} = enum\n"
        for var in definition:
            result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var},\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name}* = ptr {name}\n"

        return result

    def generate_debug(self, debug: bool) -> str:
        return f"const SPT_DEBUG = {str(debug).lower()}"

    def generate_seed(self, seed: int) -> str:
        return f"const SPT_SEED = {hex(seed)}"

    def generate_stub(self, name: str, params: dict, fhash: int) -> str:
        # Build function param declaration
        stub = f"proc {name}*("
        args = list()

        # Loop function params
        for p in params.get("params", []):
            # Register each type var
            self.type_defined.add(p["type"])
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

    def __generate_typedefs(self, name: str, entry: dict) -> str:
        typedef_code = ""
        dependencies = entry.get("dependencies", [])

        # Resolve dependencies first
        if len(dependencies) > 0:
            for dep in dependencies:
                # Avoid defining external types
                if self.__definitions.get(dep) is not None:
                    typedef_code += self.__generate_typedefs(
                        dep, self.__definitions.get(dep)
                    )

        # Generate correct entry type
        type_ = entry.get("type")
        if type_ == "struct":
            typedef_code += self.generate_struct(name, entry.get("definition", []))
        elif type_ == "enum":
            typedef_code += self.generate_enum(name, entry.get("definition", []))
        elif type_ == "union":
            typedef_code += self.generate_union(name, entry.get("definition", []))
        elif type_ == "pointer":
            typedef_code += self.generate_pointer(name, entry.get("definition", []))
        elif type_ == "standard":
            typedef_code += self.generate_standard(name, entry.get("definition", []))
        elif type_ is None:
            raise NotImplementedError(f"Missing {name} type")
        else:
            raise NotImplementedError("Unsupported definition type")

        return typedef_code

    def generate_definitions(self) -> str:
        code = ""
        for name in self.type_defined:
            # If Winim already share this structure
            if f"{name}*" in self.__winimdef:
                continue

            entry = self.__definitions.get(name)
            # Search for pointers
            if entry is None:
                name = name[1:]
                entry = self.__definitions.get(name)

            # Still nothing... it might be a standard struct then
            if entry is None:
                continue

            code += self.__generate_typedefs(name, entry)

        return code
