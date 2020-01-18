import unittest
import zinc_cli.commands.zinc_create as zinc_create


class TestZincCreate(unittest.TestCase):
    def test_can_create(self):
        zinc_create.create_project("name")
        pass
