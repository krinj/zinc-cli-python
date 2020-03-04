import kix

from .create_contact_api_request import CreateContactApiRequest
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def create_contact_api(request: CreateContactApiRequest):

    kix.info("Creating Contact API")

    # Return the instructions to CFN.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    service_model.project_name.set(request.project_name)
    service_model.forwarding_email.set(request.forwarding_email)
    service_model.create_contact_api.set(True)
    return service_model
