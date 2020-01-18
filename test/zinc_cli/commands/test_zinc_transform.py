import unittest
import zinc_cli.commands.zinc_transform as zinc_transform
from test.testing_utils import redirect_output


class TestZincTransform(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        redirect_output()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test_can_transform(self):
        zinc_transform.transform_project()
        pass
