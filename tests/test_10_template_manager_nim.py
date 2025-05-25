# -*- coding: utf-8 -*-

import unittest

import importlib.resources as pkg_resources

from sysplant import templates as pkg_templates

from sysplant.managers.templateManager import TemplateManager


class TestAbstract(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)

    def test_00_init(self):
        TemplateManager(language="nim")

    def test_01_str(self):
        klass = TemplateManager(language="nim")

        with pkg_resources.files(pkg_templates).joinpath("base.nim").open("r") as file:
            self.assertEqual(str(klass), file.read())

    def test_02_load_stub(self):
        klass = TemplateManager(language="nim")
