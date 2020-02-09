import kix

from .create_crud_api_request import CreateCrudApiRequest
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def create_crud_api(request: CreateCrudApiRequest):

    kix.info("Creating CRUD API")

    # Return the instructions to CFN.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    service_model.project_name.set(request.project_name)
    service_model.create_crud_api.set(True)
    return service_model
