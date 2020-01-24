import os
import unittest
import zinc_cli.commands.zinc_create as zinc_create
from test.testing_utils import redirect_output
import sys


class TestZincCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        redirect_output()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test_can_create(self):
        app_name = sys.argv[0]
        command_args = "--name integtest --static-site zinccli.com"
        sys.argv = [app_name, *command_args.split(" ")]
        print(sys.argv)
        zinc_create.invoke()
        pass
