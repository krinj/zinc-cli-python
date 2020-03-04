# This function creates a project the same way like a React project.


from zinc_cli.commands.aws_util.aws_utils import create_aws_service_model, bootstrap_cdk
from zinc_cli.commands.create.contact_api.create_contact_api_cmd import create_contact_api
from zinc_cli.commands.create.contact_api.create_contact_api_request import CreateContactApiRequest
from zinc_cli.commands.create.create_infrastructure import create_infrastructure
from zinc_cli.commands.create.project.create_project_cmd import create_project
from zinc_cli.commands.create.project.create_project_request import CreateProjectRequest
from zinc_cli.commands.create.static_site.create_static_site_cmd import create_static_site
from zinc_cli.commands.create.static_site.create_static_site_request import CreateStaticSiteRequest
from zinc_cli.commands.create.zinc_create_request import ZincCreateRequest
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def invoke():

    master_request: ZincCreateRequest = ZincCreateRequest().gather_arguments()

    # Create local resources and template site.
    bucket_name = f"static.{master_request.domain}"
    project_request = CreateProjectRequest(
        project_name=master_request.project_name,
        domain_name=master_request.domain,
        bucket_name=bucket_name,
        dry_run=master_request.dry_run
    )
    create_project(project_request)

    # AWS Validation.
    service_model: InfrastructureServiceModel = create_aws_service_model()

    # Ensure that CDK is bootstrapped.
    bootstrap_cdk(service_model.aws_account_id.value, service_model.aws_region.value)

    # Add the static site request to the service model.
    static_site_request = CreateStaticSiteRequest(master_request.project_name, master_request.domain, bucket_name)
    service_model.append(create_static_site(static_site_request))

    # Add Contact Form API to the service model.
    if master_request.with_contact_api:
        contact_api_request = CreateContactApiRequest(
            project_name=master_request.project_name,
            forwarding_email=master_request.forwarding_email
        )
        service_model.append(create_contact_api(contact_api_request))

    # Create service infrastructure.
    create_infrastructure(service_model, master_request.dry_run)

