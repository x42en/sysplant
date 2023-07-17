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

        # Adapt module based on what to load
        raw = pkg_resources.open_text(pkg_module, name)
        return raw.read()

    def __load_definitions(self) -> None:
        """
        Private method used to load the definitions file containing all the windows type definitions not set by NIM or winim
        """
        # Load supported functions definitions
        data = self.__load_template(pkg_data, "definitions.json")
        self.__definitions = json.loads(data)

    def __load_winimdef(self) -> None:
        """
        Private method used to load the winim library file responsible for type definition. This prevent duplicate definitions.
        This file might be updated regularly until all the types are integrated inside Winim library (PR to do)
        """
        # Load supported functions definitions
        self.__winimdef = self.__load_template(pkg_data, "windef.nim")

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
                if self.is_generated(dep):
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
        self.register_definition(name)

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
            if f"{name}*" in self.__winimdef:
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
            if self.is_generated(name):
                continue

            code += self.__generate_typedefs(name, entry)

        return code
