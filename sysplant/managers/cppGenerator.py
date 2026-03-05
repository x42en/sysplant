# -*- coding:utf-8 -*-


from sysplant.managers.cGenerator import CGenerator


class CppGenerator(CGenerator):
    """
    Main class responsible for C++ code generation.

    C++ is fully backward-compatible with the C-style typedef struct,
    union, enum, and GCC inline assembly used by CGenerator.
    This subclass inherits all generation methods unchanged.
    """

    pass
