# -*- coding:utf-8 -*-


from sysplant.abstracts.abstractGenerator import AbstractGenerator
from sysplant.constants.sysplantConstants import SysPlantConstants


class RustGenerator(AbstractGenerator):
    """
    Main class responsible for Rust code generation
    """

    def __init__(self) -> None:
        super().__init__()
        self.__functions = dict()

    def generate_struct(self, name: str, definition: list) -> str:
        """
        Public method used to generate a Rust basic structure.
        The structure will be generated as a repr(C) pub struct.
        A pointer type alias will always be generated in the form of: P+NAME

        Args:
            name (str): Structure name
            definition (list): Structure parameters from definitions.json

        Returns:
            str: Rust code for basic structure definition
        """
        result = f"#[repr(C)]\npub struct {name} {{\n"
        for var in definition:
            if len(var) == 2:
                result += f"{SysPlantConstants.RUST_TAB}pub {var[1]}: {var[0]},\n"
            elif len(var) == 3:
                # Rust doesn't have native bitfields, use comment to document
                result += f"{SysPlantConstants.RUST_TAB}pub {var[1]}: {var[0]}, // bitsize: {var[2]}\n"
        result += "}\n"
        # Always add pointer type
        result += f"pub type P{name} = *mut {name};\n"

        return result

    def generate_union(self, name: str, definition: list) -> str:
        """
        Public method used to generate Rust union when a parent needs it.
        A pointer type alias will always be generated in the form of: P+NAME

        Args:
            name (str): Union name
            definition (list): Union parameters from definitions.json

        Returns:
            str: Rust code for union definition
        """
        result = f"#[repr(C)]\npub union {name} {{\n"
        for var in definition:
            if len(var) == 2:
                result += f"{SysPlantConstants.RUST_TAB}pub {var[1]}: {var[0]},\n"
            elif len(var) == 3:
                result += f"{SysPlantConstants.RUST_TAB}pub {var[1]}: {var[0]}, // bitsize: {var[2]}\n"
        result += "}\n"
        # Always add pointer type
        result += f"pub type P{name} = *mut {name};\n"

        return result

    def generate_pointer(self, name: str, definition: list) -> str:
        """
        Public method used to generate Rust pointer type alias.

        Args:
            name (str): Pointer name
            definition (list): Type definition to point to from definitions.json

        Returns:
            str: Rust code for pointer type alias
        """
        result = f"pub type {name} = *mut {definition[0]};\n"
        return result

    def generate_standard(self, name: str, definition: list) -> str:
        """
        Public method used to generate Rust type alias declaration.
        A pointer type alias will always be generated in the form of: P+NAME

        Args:
            name (str): Type alias name
            definition (list): Base type from definitions.json

        Returns:
            str: Rust code for type alias definition
        """
        result = f"pub type {name} = {definition[0]};\n"
        # Always add pointer type
        result += f"pub type P{name} = *mut {name};\n"
        return result

    def generate_enum(self, name: str, definition: list) -> str:
        """
        Public method used to generate Rust enum declaration.
        A pointer type alias will always be generated in the form of: P+NAME

        Args:
            name (str): Enum name
            definition (list): Enum entries from definitions.json

        Returns:
            str: Rust code for enum definition
        """
        result = f"#[repr(C)]\npub enum {name} {{\n"
        for var in definition:
            result += f"{SysPlantConstants.RUST_TAB}{var},\n"
        result += "}\n"
        # Always add pointer type
        result += f"pub type P{name} = *mut {name};\n"

        return result

    def generate_debug(self, debug: bool) -> str:
        """
        Public method used to generate the SPT_DEBUG constant flag

        Args:
            debug (bool): Debug flag value

        Returns:
            str: Rust code for template integration
        """
        return f"const SPT_DEBUG: bool = {str(debug).lower()};"

    def generate_seed(self, seed: int) -> str:
        """
        Public method used to generate the SPT_SEED constant value

        Args:
            seed (int): Seed value

        Returns:
            str: Rust code for template integration
        """
        return f"const SPT_SEED: u32 = {hex(seed)};"

    def generate_stub(self, name: str, params: dict, fhash: int) -> str:
        """
        Public method used to generate stub code of syscall to hook

        Args:
            name (str): NtFunction name to hook
            params (dict): Parameters of functions defined in prototypes.json
            fhash (int): NtFunction hash value used by ASM call

        Returns:
            str: Rust code for template integration
        """
        self.__functions[name] = params

        # Build global_asm stub
        # For x64: push imm32 is sign-extended, LLVM rejects unsigned values > 0x7FFFFFFF
        # Convert to negative signed representation for assembler compatibility
        if fhash > 0x7FFFFFFF:
            asm_hash = hex(fhash - 0x100000000)
        else:
            asm_hash = hex(fhash)

        stub = f'global_asm!("{name}:",\n'
        stub += f'{SysPlantConstants.RUST_TAB}"push {asm_hash}",\n'
        stub += f'{SysPlantConstants.RUST_TAB}"call SPT_Syscall",\n'
        stub += ");\n"

        return stub

    def generate_definitions(self) -> str:
        """
        Public method used to generate all required type definitions and extern function declarations.

        Returns:
            str: Rust code for template integration
        """
        func_def = ""

        # Generate extern function declarations
        if self.__functions:
            func_def += 'unsafe extern "C" {\n'
            for name, params in self.__functions.items():
                # Loop function params
                stub_items = list()
                for p in params.get("params", []):
                    # Register each type var
                    self.type_set.add(p["type"])
                    stub_items.append(
                        f"{SysPlantConstants.RUST_TAB}{SysPlantConstants.RUST_TAB}{p['name']}: {p['type']}"
                    )

                # Build function params
                func_def += (
                    f"{SysPlantConstants.RUST_TAB}pub fn {name}(\n"
                    + ",\n".join(stub_items)
                    + "\n"
                    + f"{SysPlantConstants.RUST_TAB}) -> NTSTATUS;\n"
                )
            func_def += "}\n"

        # Prepend structs definitions
        definitions = super().generate_definitions() + f"\n{func_def}"

        return definitions
