# This function creates a project the same way like a React project.

import os
import subprocess
import kix

from zinc_cli.commands.aws_util.aws_utils import create_aws_service_model, bootstrap_cdk
from zinc_cli.commands.create.project.create_project_cmd import create_project
from zinc_cli.commands.create.project.create_project_request import CreateProjectRequest
from zinc_cli.commands.create.static_site.create_static_site_cmd import create_static_site
from zinc_cli.commands.create.static_site.create_static_site_request import CreateStaticSiteRequest
from zinc_cli.commands.create.zinc_create_request import ZincCreateRequest
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def invoke():

    master_request: ZincCreateRequest = ZincCreateRequest()

    # Create local resources and template site.
    bucket_name = f"static.{master_request.domain}"
    project_request = CreateProjectRequest(project_name=master_request.project_name, bucket_name=bucket_name)
    create_project(project_request)

    # AWS Validation.
    service_model: InfrastructureServiceModel = create_aws_service_model()

    # Ensure that CDK is bootstrapped.
    bootstrap_cdk(service_model.aws_account_id.value, service_model.aws_region.value)

    # Add the static site request to the service model.
    static_site_request = CreateStaticSiteRequest(master_request.project_name, master_request.domain, bucket_name)
    service_model.append(create_static_site(static_site_request))

    # Create service infrastructure.
    create_infrastructure(service_model, master_request.dry_run)


def create_infrastructure(service_model: InfrastructureServiceModel, dry_run: bool):

    # Switch to infrastructure directory.
    current_path = _switch_to_infrastructure_path()

    # Create the infrastructure.
    _execute_infrastructure_command(dry_run, service_model)

    # Return to the previous path.
    os.chdir(current_path)
    kix.info(f"Execution Complete. Changed directory back to {current_path}.")


def _execute_infrastructure_command(dry_run, service_model):

    # Assemble the command.
    env_map = service_model.get_command_line_dict()
    deploy_command = "deploy" if dry_run is False else "synth"
    final_command = f"cdk {deploy_command} --require-approval never"
    kix.info(f"Executing command: {final_command}")

    # Prepare the environment variables for the sub process.
    env_map.update(os.environ.copy())

    # Run the command.
    result = subprocess.run(final_command.split(" "), env=env_map)
    kix.info(f"Executed result: {result}")


def _switch_to_infrastructure_path():
    module_path = os.path.dirname(__file__)
    current_path = os.getcwd()
    infrastructure_path = os.path.join(module_path, "..", "..", "infrastructure")
    os.chdir(infrastructure_path)
    kix.info(f"Changed directory to {infrastructure_path} to execute CDK.")
    return current_path
