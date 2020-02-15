import os
import unittest
from test.testing_utils import redirect_output, clear_output


class TestCreateCrudApi(unittest.TestCase):

    ORIGINAL_DIR = os.getcwd()
    SHOULD_CLEAR = False

    @classmethod
    def setUpClass(cls) -> None:
        redirect_output()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.SHOULD_CLEAR:
            clear_output(cls.ORIGINAL_DIR)

    def test_create_project_cmd(self):
        pass
