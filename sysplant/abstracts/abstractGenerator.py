# -*- coding:utf-8 -*-

import logging
import json

import importlib.resources as pkg_resources

from sysplant import data as pkg_data

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

        # Store definitions to defined
        self.type_set = set()
        self.__generated = set()
        self.__definitions: dict = {}
        self.__extra_definitions: str = ""

        try:
            # Alaways load prototypes & typedefinitions
            self.__load_definitions()
        except Exception as err:
            raise SystemError(f"Unable to load mandatory data in C Generator: {err}")

    def __load_template(self, pkg_module: str, name: str) -> str:
        """Private method used to retrieve specific data file from package module

        Args:
            pkg_module (str): The package module containing filename to request
            name (str): Filename to request

        Raises:
            ValueError: Error raised if name is None
            ValueError: Error raised if name contains forbidden chars

        Returns:
            str: Return the file content (text mode)
        """
        if name is None:
            raise ValueError("Template name can not be null")

        # Check only extension dot is set
        if not name.replace(".", "", 1).isalpha():
            raise ValueError("Invalid template name")

        # Use the new files() API instead of open_text
        with pkg_resources.files(pkg_module).joinpath(name).open("r") as f:
            return f.read()

    def __load_definitions(self) -> None:
        """
        Private method used to load the definitions file containing all the windows type definitions not set by C
        """
        # Load supported functions definitions
        data = self.__load_template(pkg_data, "definitions.json")
        self.__definitions = json.loads(data)

    def set_extra_definitions(self, name: str) -> None:
        self.__extra_definitions = self.__load_template(pkg_data, name)

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
    def generate_seed(self, name: str) -> str:
        raise NotImplementedError("Seed generation not implemented yet")

    @abstractmethod
    def generate_stub(self, name: str, params: dict, fhash: int) -> str:
        raise NotImplementedError("Stub generation not implemented yet")

    @abstractmethod
    def generate_definitions(self) -> str:
        raise NotImplementedError("Type definition generation not implemented yet")

    def __generate_typedefs(self, name: str, entry: dict) -> str:
        """
        Private method used to generate appropriate definition code based on entry type

        Args:
            name (str): Object name to define
            entry (dict): Entry associated with requested name from definitions.json that gives details about the object to generate

        Raises:
            NotImplementedError: Error raised if name is None
            NotImplementedError: Error raised if entry type is not supported. Not in : structure|enum|union|pointer|standard

        Returns:
            str: NIM code for object declaration
        """
        typedef_code = ""
        dependencies = entry.get("dependencies", [])

        # Resolve dependencies first
        if len(dependencies) > 0:
            for dep in dependencies:
                # Avoid duplicate generation
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

        # Register definitions generated
        self.__generated.add(name)

        return typedef_code

    def generate_definitions(self) -> str:
        """
        Public method used to generate all required definitions by hooked syscall.
        It will first loop through the required functions to hook, extract all parameters type to declare
        and call the private __generate_typedefs function to generate the associated code block.
        Once all chained it will return the complete code block to integrate in template

        Returns:
            str: NIM code for template integration
        """
        code = ""
        for name in self.type_set:
            # If Winim already share this structure
            if f"{name}*" in self.__extra_definitions:
                continue

            entry = self.__definitions.get(name)

            # Search pointer definition
            if entry is None:
                name = name[1:]
                entry = self.__definitions.get(name)

            # Still nothing... it might be a standard struct then
            if entry is None:
                continue

            # Avoid duplicate generation
            if name in self.__generated:
                continue

            code += self.__generate_typedefs(name, entry)

        return code
