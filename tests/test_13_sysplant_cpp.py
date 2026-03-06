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


class TestSysplantCpp(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)

    def test_00_init(self):
        Sysplant(language="cpp")

    def test_02_generate_direct(self):
        klass = Sysplant(language="cpp")
        result = klass.generate(
            iterator="syswhispers", method="direct", syscalls="common"
        )

        # C++ templates fallback to .c files for iterators/resolvers/stubs
        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.c").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        with pkg_resources.files(pkg_resolvers).joinpath("number.c").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        with pkg_resources.files(pkg_stubs).joinpath("direct_x64.c").open("r") as stub:
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("    ##__DEBUG_INT__## \\n\\\n", "")
            self.assertIn(clean_stub, result)

    def test_02_generate_indirect(self):
        klass = Sysplant(language="cpp")
        result = klass.generate(
            iterator="syswhispers", method="indirect", syscalls="common"
        )

        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.c").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        with pkg_resources.files(pkg_resolvers).joinpath("basic.c").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        with pkg_resources.files(pkg_stubs).joinpath("indirect_x64.c").open(
            "r"
        ) as stub:
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("    ##__DEBUG_INT__## \\n\\\n", "")
            self.assertIn(clean_stub, result)

    def test_02_generate_random(self):
        klass = Sysplant(language="cpp")
        result = klass.generate(
            iterator="syswhispers", method="random", syscalls="common"
        )

        with pkg_resources.files(pkg_iterators).joinpath("syswhispers.c").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        with pkg_resources.files(pkg_resolvers).joinpath("number.c").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        with pkg_resources.files(pkg_resolvers).joinpath("random.c").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        with pkg_resources.files(pkg_stubs).joinpath("random_x64.c").open("r") as stub:
            clean_stub = stub.read().replace("##__SYSCALL_INT__##", "syscall")
            clean_stub = clean_stub.replace("    ##__DEBUG_INT__## \\n\\\n", "")
            self.assertIn(clean_stub, result)

    def test_02_generate_egg_hunter(self):
        klass = Sysplant(language="cpp")
        result = klass.generate(
            iterator="canterlot", method="egg_hunter", syscalls="common"
        )

        with pkg_resources.files(pkg_iterators).joinpath("canterlot.c").open(
            "r"
        ) as iterator:
            self.assertIn(iterator.read(), result)

        with pkg_resources.files(pkg_resolvers).joinpath("number.c").open(
            "r"
        ) as resolver:
            self.assertIn(resolver.read(), result)

        # Ensure no literal 'syscall' instruction in the output
        self.assertNotIn("    syscall \\n\\\n", result)

        # Ensure sanitizer function is present
        self.assertIn("SPT_SanitizeSyscalls", result)

        # Ensure egg pattern arrays are present
        self.assertIn("SPT_EGG_PATTERN", result)
        self.assertIn("SPT_EGG_REPLACE", result)

        # Ensure .byte directives are present (egg marker in stub)
        self.assertIn(".byte 0x", result)

    def test_03_scramble_direct(self):
        klass = Sysplant(language="cpp")
        klass.generate(iterator="freshy", method="direct", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_03_scramble_indirect(self):
        klass = Sysplant(language="cpp")
        klass.generate(iterator="syswhispers", method="indirect", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_03_scramble_random(self):
        klass = Sysplant(language="cpp")
        klass.generate(iterator="canterlot", method="random", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_03_scramble_egg_hunter(self):
        klass = Sysplant(language="cpp")
        klass.generate(iterator="canterlot", method="egg_hunter", syscalls="common")
        result = klass.scramble(True)

        for entry in SysPlantConstants.INTERNAL_FUNCTIONS:
            self.assertNotIn(entry, result)

    def test_04_output(self):
        klass = Sysplant(language="cpp")
        klass.generate(iterator="canterlot", method="direct", syscalls="common")
        (_, filename) = tempfile.mkstemp(text=True)
        result = klass.output(filename)

        with open(f"{filename}.hpp", "r") as raw:
            self.assertEqual(result, raw.read())

    def test_05_base_uses_alloca(self):
        """Verify the C++ base template uses alloca() instead of VLA."""
        klass = Sysplant(language="cpp")
        result = klass.generate(iterator="hell", method="direct", syscalls="common")
        self.assertIn("alloca", result)
        # Ensure no VLA pattern from the C template
        self.assertNotIn("char string_to_hash[sizeof", result)

    def test_06_base_uses_wincrypt(self):
        """Verify the C++ base template uses Windows CryptoAPI instead of custom MD5."""
        klass = Sysplant(language="cpp")
        result = klass.generate(iterator="hell", method="direct", syscalls="common")
        # CryptoAPI calls must be present
        self.assertIn("CryptAcquireContext", result)
        self.assertIn("CryptCreateHash", result)
        self.assertIn("CryptHashData", result)
        self.assertIn("wincrypt.h", result)
        # Custom MD5 implementation must NOT be present
        self.assertNotIn("SPT_HashInit", result)
        self.assertNotIn("SPT_HashUpdate", result)
        self.assertNotIn("SPT_HashFinalize", result)
        self.assertNotIn("SPT_HashStep", result)
        self.assertNotIn("SPT_HashContext", result)
