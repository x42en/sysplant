# -*- coding: utf-8 -*-

import string
import unittest

from sysplant.abstracts.abstractFactory import AbstractFactory
from sysplant.constants.sysplantConstants import SysPlantConstants


class TestAbstract(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)

    def test_00_init(self):
        AbstractFactory()

    def test_01_generate_random_seed(self):
        klass = AbstractFactory()
        seed = klass.generate_random_seed()
        self.assertEqual(type(seed), int)
        self.assertIn(seed, range((2**28), (2**32)))

    def test_02_generate_random_string(self):
        klass = AbstractFactory()
        size = 4
        result = klass.generate_random_string(size)
        self.assertEqual(type(result), str)
        self.assertEqual(len(result), size)
        for letter in result:
            self.assertIn(letter, string.ascii_letters)

    def test_02_generate_random_range(self):
        klass = AbstractFactory()
        choices = ["a", ":", "!", "_", "b", "?", "f", 8, 9, 0x0F, 0x00]
        result = klass.generate_random_string(6, choices)
        self.assertEqual(type(result), str)
        clean = [str(x) for x in choices]
        for letter in result:
            self.assertIn(letter, "".join(clean))

    def test_03_get_function_hash(self):
        klass = AbstractFactory()
        hash_value = klass.get_function_hash(55, "NtProtectVirtualMemory")
        self.assertEqual(type(hash_value), int)
        self.assertEqual(len(str(hash_value)), 10)

        hash_kernel = klass.get_function_hash(55, "ZwProtectVirtualMemory")
        self.assertEqual(hash_value, hash_kernel)

    def test_04_replace_nothing(self):
        klass = AbstractFactory()
        raw = "Simple text without tag"
        klass.data = raw

        klass.replace_tag("tag", "foo")
        self.assertEqual(type(klass.data), str)
        self.assertEqual(klass.data, raw)

    def test_04_replace_tag(self):
        klass = AbstractFactory()
        raw = f"Simple text with {SysPlantConstants.TAG_START}TEST_TAG{SysPlantConstants.TAG_END} to replace"
        klass.data = raw

        klass.replace_tag("TEST_TAG", "foo")
        self.assertEqual(type(klass.data), str)
        self.assertEqual(klass.data, "Simple text with foo to replace")

    def test_05_remove_tag(self):
        klass = AbstractFactory()
        raw = f"Simple tag to remove: {SysPlantConstants.TAG_START}TEST_TAG{SysPlantConstants.TAG_END}"
        klass.data = raw

        klass.remove_tag("TEST_TAG")
        self.assertEqual(type(klass.data), str)
        self.assertEqual(klass.data, "Simple tag to remove:")

    def test_06_remove_tag_multilines(self):
        klass = AbstractFactory()
        raw = f"A line\n{SysPlantConstants.TAG_START}TEST_TAG{SysPlantConstants.TAG_END}\nAnother line"
        klass.data = raw

        klass.remove_tag("TEST_TAG")
        self.assertEqual(type(klass.data), str)
        self.assertEqual(klass.data, "A line\nAnother line")

    def test_06_remove_tag_multilines_spaced(self):
        klass = AbstractFactory()
        raw = f"""
A line not indented
    An indented line
    {SysPlantConstants.TAG_START}TEST_TAG{SysPlantConstants.TAG_END}
    Another indentation
End of text
"""
        klass.data = raw

        klass.remove_tag("TEST_TAG")
        self.assertEqual(type(klass.data), str)
        clean = """
A line not indented
    An indented line
    Another indentation
End of text
"""
        self.assertEqual(klass.data, clean)
