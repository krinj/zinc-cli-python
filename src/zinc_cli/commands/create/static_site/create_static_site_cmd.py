import kix

from .create_static_site_request import CreateStaticSiteRequest
from zinc_cli.commands.create.domain.domain_manager import DomainManager
from zinc_cli.commands.create.domain.hosted_zone_manager import HostedZoneManager
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def create_static_site(request: CreateStaticSiteRequest):

    kix.info(f"Creating Static Site: {request.domain_name}")

    # Ensure the hosted zone.
    if not HostedZoneManager.has_hosted_zone(request.domain_name):
        kix.error(f"No hosted zone detected for {request.domain_name}."
                     f"Please ensure you have created a HostedZone for this domain on your AWS account.")
        raise Exception(f"No hosted zone on AWS account for {request.domain_name}")

    # Ensure the domain.
    if not DomainManager.validate(request.domain_name):
        raise Exception(f"Not a valid domain name: {request.domain_name}")

    if not DomainManager.user_owns_domain(request.domain_name):
        kix.warning(f"You do not own the domain {request.domain_name}. "
                    f"You will need to configure the domain's name servers to redirect the traffic.")

    # Return the instructions to CFN.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    service_model.create_static_site.set(True)
    service_model.domain_name.set(request.domain_name)
    service_model.project_name.set(request.project_name)
    service_model.static_site_bucket_name.set(request.bucket_name)
    return service_model
