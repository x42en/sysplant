# -*- coding:utf-8 -*-


from sysplant.abstracts.abstractGenerator import AbstractGenerator
from sysplant.constants.sysplantConstants import SysPlantConstants


class CGenerator(AbstractGenerator):
    """
    Main class responsible for C code generation
    """

    def __init__(self) -> None:
        super().__init__()
        self.__functions = dict()

    def generate_struct(self, name: str, definition: list) -> str:
        """
        Public method used to generate a C basic structure.
        The structure will be generated as a public object for external code usages.
        A pointer to the structure will always be generated in the form of: *P+NAME

        Args:
            name (str): Structure name
            definition (list): Structure parameters from definitions.json

        Returns:
            str: C code for basic structure definition (except type keyword for definition chaining)
        """
        result = f"#ifndef {name}\ntypedef struct _{name}\n" + "{\n"
        for var in definition:
            if len(var) == 2:
                result += f"{SysPlantConstants.C_TAB}{var[0]} {var[1]};\n"

            elif len(var) == 3:
                result += f"{SysPlantConstants.C_TAB}{var[0]} {var[1]} = {var[2]};\n"
        # Always add pointer
        result += "}" + f" {name}, *P{name};\n#endif\n"

        return result

    def generate_union(self, name: str, definition: list) -> str:
        """
        Public method used to generate C union structure when a parent needs it.
        This structure will be generated as a private object as it won't be directly accessed by external code.
        A pointer to the union structure will always be generated in the form of: *P+NAME

        Args:
            name (str): Union structure name
            definition (list): Union structure parameters from definitions.json

        Returns:
            str: C code for union structure definition (except type keyword for definition chaining)
        """
        result = f"#ifndef {name}\ntypedef union _{name}\n" + "{\n"
        for var in definition:
            if len(var) == 2:
                result += f"{SysPlantConstants.C_TAB}{var[0]} {var[1]};\n"

            elif len(var) == 3:
                result += f"{SysPlantConstants.C_TAB}{var[0]} {var[1]} = {var[2]};\n"
        # Always add pointer
        result += "}" + f" {name}, *P{name};\n#endif\n"

        return result

    def generate_pointer(self, name: str, definition: list) -> str:
        """
        Public method used to generate C pointer to defined var
        The pointer will be geneerated as a public object for external code usages.

        Args:
            name (str): Pointer name
            definition (list): Type definition to point to from definitions.json

        Returns:
            str: C code for standard pointer declaration
        """
        result = f"typedef {name}* {definition[0]};\n"
        return result

    def generate_standard(self, name: str, definition: list) -> str:
        """
        Public method used to generate C varaiable declaration.
        The variable will be generated as a public object for external code usages.
        A pointer to the variable will always be generated in the form of: P+NAME

        Args:
            name (str): Variable name
            definition (list): Variable type from definitions.json

        Returns:
            str: C code for variable definition (except type keyword for definition chaining)
        """
        result = f"typedef {name}* = {definition[0]};\n"
        # Always add pointer
        result += f"{SysPlantConstants.C_TAB}P{name}* = ptr {name};\n"
        return result

    def generate_enum(self, name: str, definition: list) -> str:
        """
        Public method used to generate C enum declaration.
        The enum structure will be generated as a public object for external code usages.
        A pointer to the enum structure will always be generated in the form of: P+NAME

        Args:
            name (str): Enum structure name
            definition (list): Enum structure entries from definitions.json

        Returns:
            str: C code for enum structure (except type keyword for definition chaining)
        """
        result = f"#ifndef {name}\ntypedef enum _{name}\n" + "{\n"
        for var in definition:
            result += f"{SysPlantConstants.C_TAB}{var},\n"
        # Always add pointer
        result += "}" + f" {name}, *P{name};\n#endif\n"

        return result

    def generate_debug(self, debug: bool) -> str:
        """
        Public method used to generate the SPT_DEBUG constant flag

        Args:
            debug (bool): Debug flag value

        Returns:
            str: C code for template integration
        """
        return f"#define SPT_DEBUG {str(debug).upper()}"

    def generate_seed(self, seed: int) -> str:
        """
        Public method used to generate the SPT_SEED constant value

        Args:
            seed (int): Seed value

        Returns:
            str: C code for template integration
        """
        return f"#define SPT_SEED {hex(seed)}"

    def generate_stub(self, name: str, params: dict, fhash: int) -> str:
        """
        Public method used to generate stub code of syscall to hook

        Args:
            name (str): NtFunction name to hook
            params (dict): Parameters of functions defined in prototypes.json
            fhash (int): NtFunction hash value used by ASM call

        Returns:
            str: C code for template integration
        """
        self.__functions[name] = params

        # Build function param declaration
        stub = f"#define {name} {name}\n"
        stub += f'__asm__("{name}: \\n\\\n'
        stub += f"{SysPlantConstants.C_TAB}push dword ptr {hex(fhash)} \\n\\\n"
        stub += f"{SysPlantConstants.C_TAB}call SPT_Syscall \\n\\\n"
        stub += '");\n'

        return stub

    def generate_definitions(self) -> str:
        func_def = ""

        # Generate function declarations
        for name, params in self.__functions.items():
            # Loop function params
            stub_items = list()
            for p in params.get("params", []):
                # Register each type var
                self.type_set.add(p["type"])
                if p.get("in", False):
                    stub_items.append(
                        f"{SysPlantConstants.C_TAB}IN {p['type']} {p['name']}"
                    )
                else:
                    stub_items.append(
                        f"{SysPlantConstants.C_TAB}OUT {p['type']} {p['name']}"
                    )

            # Build function params
            func_def += (
                f"EXTERN_C NTSTATUS {name}(\n" + ",\n".join(stub_items) + "\n);\n"
            )

        # Prepend structs definitions
        definitions = super().generate_definitions() + f"\n{func_def}"

        return definitions
