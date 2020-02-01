# This function creates a project the same way like a React project.
import argparse
import os
import subprocess

import kix

from .aws_util.aws_utils import ensure_aws_access
from .create.static_site.create_static_site_cmd import create_static_site
from .create.static_site.create_static_site_request import CreateStaticSiteRequest
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel
from zinc_cli.models.project_definition.project_definition_model import ProjectDefinitionModel


def invoke():
    print("Creating Project...")

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, required=True, help="Name of the new project.")
    parser.add_argument("--static-site", type=str, help="Bootstrap a static site at the domain.")
    parser.add_argument("--sub-domain", default="", type=str, help="Sub-domain you'd like to bootstrap.")
    parser.add_argument("--dry-run", action="store_true", help="Do not publish to actual AWS.")
    args = parser.parse_args()

    project_name = args.name
    static_site_domain = args.static_site
    sub_domain = args.sub_domain if len(args.sub_domain) > 0 else None
    dry_run = args.dry_run

    kix.info(f"Project Name: {project_name}")
    kix.info(f"Domain Name: {static_site_domain}")
    kix.info(f"Sub Domain: {sub_domain}")
    kix.info(f"Dry-run: {str(dry_run)}")

    # If local only, do not need to go past this point.

    # AWS Validation.
    service_model: InfrastructureServiceModel = ensure_aws_access()

    if static_site_domain is not None:
        request = CreateStaticSiteRequest(project_name, static_site_domain, sub_domain)
        static_site_svc_model = create_static_site(request)
        service_model.append(static_site_svc_model)

        kix.info("Bootstrapping CDK")
        bootstrap = f"cdk bootstrap aws://{service_model.aws_account_id.value}/us-east-1"
        kix.info(f"Bootstrap Command: {bootstrap}")
        os.system(bootstrap)

    create_infrastructure(service_model, dry_run)


def create_project(project_name: str):
    path = project_name

    # Check if the directory already exists.
    if os.path.exists(path):
        raise IsADirectoryError(f"Cannot create project {project_name}. "
                                f"The directory {project_name} already exists.")

    # It doesn't exist, so we can try to make the project here.
    os.mkdir(path)

    # Create a project definition and save it locally.
    project_definition_model = ProjectDefinitionModel()
    project_definition_model.model_path = path
    project_definition_model.project_name = project_name
    project_definition_model.save_to_local()

    # Try to create the table and persist the project to cloud.
    # project_definition_model.create_table()
    # project_definition_model.save_to_cloud()
    # create_infrastructure(project_name)


def create_infrastructure(service_model: InfrastructureServiceModel, dry_run: bool):
    module_path = os.path.dirname(__file__)
    current_path = os.getcwd()
    infrastructure_path = os.path.join(module_path, "..", "infrastructure")

    os.chdir(infrastructure_path)
    kix.info(f"Changed Directory to {infrastructure_path} to execute CDK.")

    env_map = service_model.get_command_line_dict()
    deploy_command = "deploy" if dry_run is False else "synth"
    final_command = f"cdk {deploy_command} --require-approval never"
    env_map.update(os.environ.copy())

    print(f"Final Command: {final_command}")
    result = subprocess.run(final_command.split(" "), env=env_map)
    print(f"Executed Result: {result}")
    os.chdir(current_path)
    print(f"Changed Directory back to {current_path}.")
