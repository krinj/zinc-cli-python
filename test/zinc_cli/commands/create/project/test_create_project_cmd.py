import os
import unittest
from test.testing_utils import redirect_output, clear_output
from zinc_cli.commands.create.project.create_project_cmd import create_project
from zinc_cli.commands.create.project.create_project_request import CreateProjectRequest


class TestCreateProjectCmd(unittest.TestCase):

    ORIGINAL_DIR = os.getcwd()
    SHOULD_CLEAR = False

    @classmethod
    def setUpClass(cls) -> None:
        redirect_output()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.SHOULD_CLEAR:
            clear_output(cls.ORIGINAL_DIR)

    def test_crate_project_cmd(self):

        # Test that we can pull a project from a repo.
        # Extract its template resource.
        # Override the deploy command.
        print("Testing Cmd")
        request = CreateProjectRequest()
        create_project(request)
