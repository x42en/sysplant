# -*- coding:utf-8 -*-

import json
from typing import Union

import importlib.resources as pkg_resources

from sysplant import data as pkg_data
from sysplant import templates as pkg_templates
from sysplant.templates import iterators as pkg_iterators
from sysplant.templates import resolvers as pkg_resolvers
from sysplant.templates import stubs as pkg_stubs

from sysplant.abstracts.abstractFactory import AbstractFactory
from sysplant.constants.sysplantConstants import SysPlantConstants


class TemplateManager(AbstractFactory):
    """
    Main class responsible for template handling
    """

    def __init__(self, language: str) -> None:
        super().__init__()
        self.__data: str = ""
        self.__prototypes: dict = {}
        self.__definitions: dict = {}
        self.__generated: set = set()
        self.__winimdef = ""

        # Define language template
        if language not in ["nim"]:
            raise NotImplementedError("Sorry language not supported ... yet ?!")
        self.__lang = language

    def __str__(self) -> str:
        return self.__data

    def __load_template(self, pkg_module: str, name: str) -> str:
        if name is None:
            raise ValueError("Template name can not be null")

        # Check only extension dot is set
        if not name.replace(".", "", 1).isalpha():
            raise ValueError("Invalid template name")

        # Adapt module based on what to load
        raw = pkg_resources.open_text(pkg_module, name)
        return raw.read()

    def __load_prototypes(self) -> None:
        # Load supported functions prototypes
        data = self.__load_template(pkg_data, "prototypes.json")
        self.__prototypes = json.loads(data)

    def __load_definitions(self) -> None:
        # Load supported functions definitions
        data = self.__load_template(pkg_data, "definitions.json")
        self.__definitions = json.loads(data)

    def __load_winimdef(self) -> None:
        # Load supported functions definitions
        self.__winimdef = self.__load_template(pkg_data, "windef.nim")

    def load_base(self) -> str:
        try:
            # Alaways load prototypes & typedefinitions
            self.__load_prototypes()
            self.__load_definitions()
            self.__load_winimdef()
        except Exception as err:
            raise SystemError(f"Unable to load mandatory data: {err}")

        try:
            # Always load initial template
            self.__data = self.__load_template(pkg_templates, f"base.{self.__lang}")
        except Exception as err:
            raise SystemError(f"Unable to load base template: {err}")

        return self.__data

    def load_stub(self, name) -> str:
        try:
            # Always load initial template
            self.__data = self.__load_template(pkg_stubs, f"{name}.{self.__lang}")
        except Exception as err:
            raise SystemError(f"Unable to load {name} stub: {err}")

        return self.__data

    def set_iterator(self, name: str) -> None:
        # Get iterator template from package
        data = self.__load_template(pkg_iterators, f"{name}.{self.__lang}")
        self.__replace_pattern("ITERATOR", data)

    def set_resolver(self, name: str) -> None:
        # Get resolver template from package
        data = self.__load_template(pkg_resolvers, f"{name}.{self.__lang}")
        self.__replace_pattern("GET_SYSCALL_ADDR", data)

    def set_seed(self, seed: int) -> None:
        if self.__lang == "nim":
            seed_code = f"const SPT_SEED = {hex(seed)}"

        # Set SEED declaration
        self.__replace_pattern("SPT_SEED", seed_code)

    def select_prototypes(self, names: Union[str, list]) -> dict:
        if names == "all":
            self.logger.info("\t. All supported functions selected", stripped=True)
            names = self.__prototypes.keys()
        elif names == "common":
            self.logger.info("\t. Common supported functions selected", stripped=True)
            names = SysPlantConstants.COMMON_SYSCALLS
        elif names == "donut":
            self.logger.info("\t. Donut functions selected", stripped=True)
            names = SysPlantConstants.DONUT_SYSCALLS
        elif type(names) is not list:
            raise ValueError("Unsupported functions type")
        else:
            self.logger.info("\t. Custom set of functions selected", stripped=True)

        self.logger.debug(f"Hooking selected functions: {','.join(names)}")
        results = dict()
        for n in names:
            proto = self.__prototypes.get(n)
            if proto is None:
                continue
            results[n] = proto

        return results

    def __generate_struct(self, name: str, definition: list) -> str:
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

    def __generate_union(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name} " + "{.pure, union.} = object\n"
        for var in definition:
            if len(var) == 2:
                result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]}: {var[0]}\n"
            elif len(var) == 3:
                result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var[1]}: {var[0]} = {var[2]}\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name} = ptr {name}\n"

        return result

    def __generate_pointer(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name}* = ptr {definition[0]}\n"
        return result

    def __generate_standard(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name}* = {definition[0]}\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name}* = ptr {name}\n"
        return result

    def __generate_enum(self, name: str, definition: list) -> str:
        result = f"{SysPlantConstants.NIM_TAB}{name}* " + "{.pure.} = enum\n"
        for var in definition:
            result += f"{SysPlantConstants.NIM_TAB}{SysPlantConstants.NIM_TAB}{var},\n"
        # Always add pointer
        result += f"{SysPlantConstants.NIM_TAB}P{name}* = ptr {name}\n"

        return result

    def __generate_typedefs(self, name: str, entry: dict) -> str:
        typedef_code = ""
        dependencies = entry.get("dependencies", [])

        # Resolve dependencies first
        if len(dependencies) > 0:
            for dep in dependencies:
                # Ensure it is not already generated
                if dep in self.__generated:
                    continue
                # Avoid defining external types
                if self.__definitions.get(dep) is not None:
                    typedef_code += self.__generate_typedefs(
                        dep, self.__definitions.get(dep)
                    )

        # Generate correct entry type
        type_ = entry.get("type")
        if type_ == "struct":
            typedef_code += self.__generate_struct(name, entry.get("definition", []))
        elif type_ == "enum":
            typedef_code += self.__generate_enum(name, entry.get("definition", []))
        elif type_ == "union":
            typedef_code += self.__generate_union(name, entry.get("definition", []))
        elif type_ == "pointer":
            typedef_code += self.__generate_pointer(name, entry.get("definition", []))
        elif type_ == "standard":
            typedef_code += self.__generate_standard(name, entry.get("definition", []))
        elif type_ is None:
            raise NotImplementedError(f"Missing {name} type")
        else:
            raise NotImplementedError("Unsupported definition type")

        # Store generated to avoid doing it twice
        self.__generated.add(name)

        return typedef_code

    def generate_definitions(self, definitions: set) -> str:
        code = ""
        for name in definitions:
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

            # Ensure it is not already generated
            if name in self.__generated:
                continue

            code += self.__generate_typedefs(name, entry)

        self.__replace_pattern("TYPE_DEFINITIONS", code)

    def replace_tag(self, name: str, content: str) -> None:
        self.__replace_pattern(name, content)

    def __replace_pattern(
        self, pattern: str, content: Union[str, int], count: int = -1
    ) -> None:
        # Replace tag with content in template data
        self.__data = self.__data.replace(
            f"{SysPlantConstants.TAG_START}{pattern}{SysPlantConstants.TAG_END}",
            str(content),
            count,
        )
