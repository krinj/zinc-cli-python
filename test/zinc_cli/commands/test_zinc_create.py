import os
import unittest
import zinc_cli.commands.zinc_create as zinc_create
from test.testing_utils import redirect_output


class TestZincCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        redirect_output()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test_can_create(self):
        zinc_create.create_project("integ_test_project")
        pass
