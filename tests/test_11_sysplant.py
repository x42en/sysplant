# -*- coding: utf-8 -*-

import os
import tempfile
import unittest
import importlib.resources as pkg_resources

from sysplant.templates import iterators as pkg_iterators
from sysplant.templates import resolvers as pkg_resolvers
from sysplant.templates import stubs as pkg_stubs

from sysplant.sysplant import Sysplant
from sysplant.constants.sysplantConstants import SysPlantConstants


class TestAbstract(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)

    def test_00_init(self):
        Sysplant()

    def test_01_list(self):
        klass = Sysplant()
        result = klass.list(os.path.join("example", "inject.nim"))
        expected = set(
            {
                "NtCreateThread",
                "NtProtectVirtualMemory",
                "NtCreateThreadEx",
                "NtAllocateVirtualMemory",
                "NtOpenProcess",
                "NtWriteVirtualMemory",
            }
        )
        self.assertEqual(type(result), set)
        self.assertEqual(result, expected)

    def test_01_list_dir(self):
        klass = Sysplant()
        result = klass.list("example")
        expected = set(
            {
                "NtCreateThread",
                "NtProtectVirtualMemory",
                "NtCreateThreadEx",
                "NtAllocateVirtualMemory",
                "NtOpenProcess",
                "NtWriteVirtualMemory",
            }
        )
        self.assertEqual(type(result), set)
        self.assertEqual(result, expected)

    def test_02_generate(self):
        klass = Sysplant()
        result = klass.generate("syswhispers", "basic", "direct", "common")

        # Ensure freshy iterator is present
        iterator = pkg_resources.open_text(pkg_iterators, "syswhispers.nim")
        self.assertIn(iterator.read(), result)

        # Ensure resolver is present
        resolver = pkg_resources.open_text(pkg_resolvers, "basic.nim")
        self.assertIn(resolver.read(), result)

        # Ensure stub is present
        stub = pkg_resources.open_text(pkg_stubs, "direct_x64.nim")
        # Correct dynamic entries
        clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
        clean_stub = clean_stub.replace("        ##__DEBUG_INT__##\n", "")

        self.assertIn(clean_stub, result)

        # Ensure generated content is valid

    def test_03_scramble_direct(self):
        klass = Sysplant()
        klass.generate("freshy", "basic", "direct", "common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_03_scramble_indirect(self):
        klass = Sysplant()
        klass.generate("canterlot", "random", "indirect", "common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_04_output(self):
        klass = Sysplant()
        klass.generate("canterlot", "basic", "direct", "common")
        (_, filename) = tempfile.mkstemp(text=True)
        result = klass.output(filename)

        with open(f"{filename}.nim", "r") as raw:
            self.assertEqual(result, raw.read())
