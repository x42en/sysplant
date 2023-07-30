# -*- coding: utf-8 -*-

import unittest

from tests.fixtures import c_output
from sysplant.managers.cGenerator import CGenerator


class TestAbstract(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)

    def test_00_init(self):
        CGenerator()

    def test_01_generate_struct(self):
        klass = CGenerator()
        definition = [
            ["PVOID", "NormalContext"],
            ["PVOID", "SystemArgument1"],
            ["PVOID", "SystemArgument2"],
        ]
        result = klass.generate_struct("KNORMAL_ROUTINE", definition)
        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.structure)

    def test_01_generate_struct3(self):
        klass = CGenerator()
        definition = [
            ["UCHAR", "WriteOutputOnExit", 1],
            ["UCHAR", "DetectManifest", 1],
            ["UCHAR", "IFEOSkipDebugger", 1],
            ["UCHAR", "IFEODoNotPropagateKeyState", 1],
            ["UCHAR", "SpareBits1", 4],
            ["UCHAR", "SpareBits2", 8],
            ["UCHAR", "ProhibitedImageCharacteristics", 16],
        ]
        result = klass.generate_struct("PS_CREATE_INFO_INIT_STATE_FLAGS", definition)
        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.structure3)

    def test_02_generate_union(self):
        klass = CGenerator()
        definition = [["ULONG_PTR", "Value"], ["PVOID", "ValuePtr"]]
        result = klass.generate_union("PS_ATTRIBUTE_UNION", definition)

        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.union)

    def test_03_generate_pointer(self):
        klass = CGenerator()
        definition = ["PVOID"]
        result = klass.generate_pointer("PPVOID", definition)

        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.pointer)

    def test_04_generate_standard(self):
        klass = CGenerator()
        definition = ["WORD"]
        result = klass.generate_standard("LANGID", definition)

        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.standard)

    def test_05_generate_enum(self):
        klass = CGenerator()
        definition = ["ViewShare = 1", "ViewUnmap = 2"]
        result = klass.generate_enum("SECTION_INHERIT", definition)

        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.enum)

    def test_06_generate_debug(self):
        klass = CGenerator()
        result = klass.generate_debug(True)

        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.debug)

    def test_07_generate_seed(self):
        klass = CGenerator()
        seed = 1
        result = klass.generate_seed(seed)

        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.seed)

    def test_08_generate_stub(self):
        klass = CGenerator()
        params = dict(
            {
                "type": "NTSTATUS",
                "lib": "ntdll.dll",
                "params": [
                    {
                        "name": "ProcessHandle",
                        "type": "HANDLE",
                        "in": True,
                        "out": False,
                        "optional": False,
                    },
                    {
                        "name": "DesiredAccess",
                        "type": "ACCESS_MASK",
                        "in": True,
                        "out": False,
                        "optional": False,
                    },
                    {
                        "name": "TokenHandle",
                        "type": "PHANDLE",
                        "in": False,
                        "out": True,
                        "optional": False,
                    },
                ],
            }
        )
        result = klass.generate_stub("NtOpenProcessToken", params, 0x5B50179B)

        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.stub)

    def test_08_generate_definitions(self):
        klass = CGenerator()
        params = dict(
            {
                "type": "NTSTATUS",
                "lib": "ntdll.dll",
                "params": [
                    {
                        "name": "ThreadHandle",
                        "type": "HANDLE",
                        "in": True,
                        "out": False,
                        "optional": False,
                    },
                    {
                        "name": "ApcRoutine",
                        "type": "PKNORMAL_ROUTINE",
                        "in": True,
                        "out": False,
                        "optional": False,
                    },
                    {
                        "name": "ApcArgument1",
                        "type": "PVOID",
                        "in": True,
                        "out": False,
                        "optional": True,
                    },
                    {
                        "name": "ApcArgument2",
                        "type": "PVOID",
                        "in": True,
                        "out": False,
                        "optional": True,
                    },
                    {
                        "name": "ApcArgument3",
                        "type": "PVOID",
                        "in": True,
                        "out": False,
                        "optional": True,
                    },
                ],
            }
        )
        klass.generate_stub("NtQueueApcThread", params, 0x5B50179B)
        result = klass.generate_definitions()

        self.assertEqual(type(result), str)
        self.assertEqual(result, c_output.definitions)
