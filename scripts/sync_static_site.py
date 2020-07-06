import zinc_cli.commands.create.zinc_create as zinc_create
from zinc_cli.commands.create.contact_api.create_contact_api_cmd import create_contact_api
from zinc_cli.commands.create.contact_api.create_contact_api_request import CreateContactApiRequest
from zinc_cli.commands.create.crud_api.create_crud_api_cmd import create_crud_api
from zinc_cli.commands.create.crud_api.create_crud_api_request import CreateCrudApiRequest
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel
from zinc_cli.commands.create.static_site.create_static_site_request import CreateStaticSiteRequest


def main():

    project_name: str = "pixiweb"
    domain_name: str = "pixiweb.net"
    bucket_name: str = "static.pixiweb.net"
    contact_form_email: str = "juangbhanich.k@gmail.com"
    is_dry_run: bool = True

    # Create the infrastructure model.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    service_model.aws_account_id.set("535707483867")
    service_model.aws_region.set("us-east-1")

    # Create the static site.
    static_site_request = CreateStaticSiteRequest(project_name, domain_name, bucket_name)
    svc_model = zinc_create.create_static_site(static_site_request)
    service_model.append(svc_model)

    # Create the contact API.
    contact_form_request = CreateContactApiRequest(project_name, forwarding_email=contact_form_email)
    svc_model = create_contact_api(contact_form_request)
    service_model.append(svc_model)

    # Create the menu API.
    crud_api_request = CreateCrudApiRequest(project_name)
    svc_model = create_crud_api(crud_api_request)
    service_model.append(svc_model)

    # Deploy the infrastructure.
    zinc_create.create_infrastructure(service_model, dry_run=is_dry_run)


if __name__ == "__main__":
    main()
