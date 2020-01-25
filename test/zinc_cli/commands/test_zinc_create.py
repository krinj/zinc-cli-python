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
        command_args = "--name ITGT100 --static-site zinccli.com --dry-run"
        sys.argv = [app_name, *command_args.split(" ")]
        print(sys.argv)
        zinc_create.invoke()
        pass

    def test_create_static_site(self):
        zinc_create.create_static_site("ITGT423", "zinccli.com", dry_run=True)
        pass
