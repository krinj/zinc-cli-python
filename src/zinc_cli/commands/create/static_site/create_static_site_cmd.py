from .create_static_site_request import CreateStaticSiteRequest
from zinc_cli.commands.create.domain.domain_manager import DomainManager
from zinc_cli.commands.create.domain.hosted_zone_manager import HostedZoneManager
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel
from logkit import log


def create_static_site(request: CreateStaticSiteRequest):

    print(f"Creating Static Site: {request.domain_name}")

    # Ensure the hosted zone.
    if not HostedZoneManager.has_hosted_zone(request.domain_name):
        log.error(f"No hosted zone detected for {request.domain_name}."
                     f"Please ensure you have created a HostedZone for this domain on your AWS account.")
        raise Exception(f"No hosted zone on AWS account for {request.domain_name}")

    # Ensure the domain.
    if not DomainManager.validate(request.domain_name):
        raise Exception(f"Not a valid domain name: {request.domain_name}")

    if not DomainManager.user_owns_domain(request.domain_name):
        log.warning(f"You do not own the domain {request.domain_name}. "
                    f"You will need to configure the domain's name servers to redirect the traffic.")

    # Return the instructions to CFN.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    service_model.static_site_root_domain.set(request.domain_name)
    service_model.project_name.set(request.project_name)
    if request.sub_domain is not None:
        service_model.static_site_sub_domain.set(request.sub_domain)
    return service_model
