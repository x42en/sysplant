# -*- coding: utf-8 -*-

import unittest

from sysplant.abstracts.abstractFactory import AbstractFactory
from sysplant.constants.sysplantConstants import SysPlantConstants


class TestAbstract(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)

        self.data = dict({"name": None})

    def test_00_init(self):
        AbstractFactory()
