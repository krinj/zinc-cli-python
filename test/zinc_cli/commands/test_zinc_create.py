import os
import unittest
import zinc_cli.commands.zinc_create as zinc_create
from zinc_cli.commands.create.crud_api.create_crud_api_request import CreateCrudApiRequest
from zinc_cli.commands.create.crud_api.create_crud_api_cmd import create_crud_api
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel
from test.testing_utils import redirect_output
import sys

from zinc_cli.commands.create.static_site.create_static_site_request import CreateStaticSiteRequest


class TestZincCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        redirect_output()

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def setUp(self) -> None:
        self.service_model: InfrastructureServiceModel = InfrastructureServiceModel()
        self.service_model.aws_account_id.set("535707483867")
        self.service_model.aws_region.set("ap-southeast-1")

    def test_can_create(self):
        app_name = sys.argv[0]
        command_args = "--name ITGT100 --static-site zinccli.com --dry-run"
        sys.argv = [app_name, *command_args.split(" ")]
        print(sys.argv)
        zinc_create.invoke()
        pass

    def test_create_static_site(self):
        request = CreateStaticSiteRequest("ITGT101", "zinccli.com", None)
        svc_model = zinc_create.create_static_site(request)
        self.service_model.append(svc_model)
        zinc_create.create_infrastructure(self.service_model, dry_run=True)

    def test_create_static_site_with_sub_domain(self):
        request = CreateStaticSiteRequest("ITGT102", "zinccli.com", "hello")
        svc_model = zinc_create.create_static_site(request)
        self.service_model.append(svc_model)
        zinc_create.create_infrastructure(self.service_model, dry_run=True)

    def test_create_site_without_zone(self):
        request = CreateStaticSiteRequest("ITGT103", "invalidzone.com", "")
        svc_model = zinc_create.create_static_site(request)
        self.service_model.append(svc_model)
        zinc_create.create_infrastructure(self.service_model, dry_run=True)

    def test_create_static_site_no_https(self):
        request = CreateStaticSiteRequest("ITGT104", "zinccli.com", None, with_https=False)
        svc_model = zinc_create.create_static_site(request)
        self.service_model.append(svc_model)
        zinc_create.create_infrastructure(self.service_model, dry_run=True)

    def test_create_crud_api(self):
        request = CreateCrudApiRequest("ITGT106")
        svc_model = create_crud_api(request)
        self.service_model.append(svc_model)
        zinc_create.create_infrastructure(self.service_model, dry_run=False)

