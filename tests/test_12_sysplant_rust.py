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


class TestSysplantRust(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)

    def test_00_init(self):
        Sysplant(language="rust")

    def test_02_generate_direct(self):
        klass = Sysplant(language="rust")
        result = klass.generate(
            iterator="syswhispers", method="direct", syscalls="common"
        )

        # Ensure syswhispers iterator is present
        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.rs").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        # Ensure resolver is present
        with pkg_resources.files(pkg_resolvers).joinpath("number.rs").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        # Ensure stub is present
        with pkg_resources.files(pkg_stubs).joinpath("direct_x64.rs").open("r") as stub:
            # Correct dynamic entries
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("    ##__DEBUG_INT__##\n", "")

            self.assertIn(clean_stub, result)

    def test_02_generate_indirect(self):
        klass = Sysplant(language="rust")
        result = klass.generate(
            iterator="syswhispers", method="indirect", syscalls="common"
        )

        # Ensure syswhispers iterator is present
        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.rs").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        # Ensure resolver is present
        with pkg_resources.files(pkg_resolvers).joinpath("basic.rs").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        # Ensure stub is present
        with pkg_resources.files(pkg_stubs).joinpath("indirect_x64.rs").open(
            "r"
        ) as stub:
            # Correct dynamic entries
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("    ##__DEBUG_INT__##\n", "")

            self.assertIn(clean_stub, result)

    def test_02_generate_random(self):
        klass = Sysplant(language="rust")
        result = klass.generate(
            iterator="syswhispers", method="random", syscalls="common"
        )

        # Ensure syswhispers iterator is present
        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.rs").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        # Ensure resolver is present
        with pkg_resources.files(pkg_resolvers).joinpath("number.rs").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        with pkg_resources.files(pkg_resolvers).joinpath("random.rs").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        # Ensure stub is present
        with pkg_resources.files(pkg_stubs).joinpath("random_x64.rs").open("r") as stub:
            # Correct dynamic entries
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("    ##__DEBUG_INT__##\n", "")

            self.assertIn(clean_stub, result)

    def test_03_scramble_direct(self):
        klass = Sysplant(language="rust")
        klass.generate(iterator="freshy", method="direct", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_03_scramble_indirect(self):
        klass = Sysplant(language="rust")
        klass.generate(iterator="syswhispers", method="indirect", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_03_scramble_random(self):
        klass = Sysplant(language="rust")
        klass.generate(iterator="canterlot", method="random", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_04_output(self):
        klass = Sysplant(language="rust")
        klass.generate(iterator="canterlot", method="direct", syscalls="common")
        (_, filename) = tempfile.mkstemp(text=True)
        result = klass.output(filename)

        with open(f"{filename}.rs", "r") as raw:
            self.assertEqual(result, raw.read())
