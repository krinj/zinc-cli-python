import os
import unittest
import commands.zinc_create as zinc_create
from test.testing_utils import redirect_output
import sys

from commands.create.static_site.create_static_site_request import CreateStaticSiteRequest


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
        request = CreateStaticSiteRequest("ITGT101", "zinccli.com", "")
        svc_model = zinc_create.create_static_site(request)
        zinc_create.create_infrastructure(svc_model, dry_run=True)

    def test_create_static_site_with_sub_domain(self):
        request = CreateStaticSiteRequest("ITGT101", "hello.zinccli.com", "")
        svc_model = zinc_create.create_static_site(request)
        zinc_create.create_infrastructure(svc_model, dry_run=True)

