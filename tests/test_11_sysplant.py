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

    def test_02_generate_direct(self):
        klass = Sysplant()
        result = klass.generate(
            iterator="syswhispers", method="direct", syscalls="common"
        )

        # Ensure freshy iterator is present
        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.nim").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        # Ensure resolver is present
        with pkg_resources.files(pkg_resolvers).joinpath("number.nim").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        # Ensure stub is present
        with pkg_resources.files(pkg_stubs).joinpath("direct_x64.nim").open(
            "r"
        ) as stub:
            # Correct dynamic entries
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("        ##__DEBUG_INT__##\n", "")

            self.assertIn(clean_stub, result)

        # Ensure generated content is valid

    def test_02_generate_indirect(self):
        klass = Sysplant()
        result = klass.generate(
            iterator="syswhispers", method="indirect", syscalls="common"
        )

        # Ensure freshy iterator is present
        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.nim").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        # Ensure resolver is present
        with pkg_resources.files(pkg_resolvers).joinpath("basic.nim").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        # Ensure stub is present
        with pkg_resources.files(pkg_stubs).joinpath("indirect_x64.nim").open(
            "r"
        ) as stub:
            # Correct dynamic entries
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("        ##__DEBUG_INT__##\n", "")

            self.assertIn(clean_stub, result)

        # Ensure generated content is valid

    def test_02_generate_random(self):
        klass = Sysplant()
        result = klass.generate(
            iterator="syswhispers", method="random", syscalls="common"
        )

        # Ensure freshy iterator is present
        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.nim").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        # Ensure resolver is present
        with pkg_resources.files(pkg_resolvers).joinpath("number.nim").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        with pkg_resources.files(pkg_resolvers).joinpath("random.nim").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        # Ensure stub is present
        with pkg_resources.files(pkg_stubs).joinpath("random_x64.nim").open(
            "r"
        ) as stub:
            # Correct dynamic entries
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("        ##__DEBUG_INT__##\n", "")

            self.assertIn(clean_stub, result)

        # Ensure generated content is valid

    def test_03_scramble_direct(self):
        klass = Sysplant()
        klass.generate(iterator="freshy", method="direct", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_03_scramble_indirect(self):
        klass = Sysplant()
        klass.generate(iterator="syswhispers", method="indirect", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_03_scramble_random(self):
        klass = Sysplant()
        klass.generate(iterator="canterlot", method="random", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_04_output(self):
        klass = Sysplant()
        klass.generate(iterator="canterlot", method="direct", syscalls="common")
        (_, filename) = tempfile.mkstemp(text=True)
        result = klass.output(filename)

        with open(f"{filename}.nim", "r") as raw:
            self.assertEqual(result, raw.read())
