from .create_static_site_request import CreateStaticSiteRequest
from ..domain.domain_manager import DomainManager
from ...aws_util.aws_utils import ensure_aws_access
from ....infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def create_static_site(request: CreateStaticSiteRequest):

    print(f"Creating Static Site: {request.domain_name}")

    # Ensure the domain.
    if not DomainManager.validate(request.domain_name):
        raise Exception(f"Not a valid domain name: {request.domain_name}")

    if not DomainManager.user_owns_domain(request.domain_name):
        raise Exception(f"You do not own this domain: {request.domain_name}. Please register it on your AWS account.")

    # Composed domain.
    final_domain: str = request.domain_name
    if request.sub_domain is not None and len(request.sub_domain) > 0:
        final_domain = f"{request.sub_domain}.{request.domain_name}"

    # Return the instructions to CFN.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    service_model.static_site_domain.set(final_domain)
    return service_model
