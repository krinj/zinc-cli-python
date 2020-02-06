# This function creates a project the same way like a React project.
import argparse
import os
import subprocess
from typing import Union

import kix

from .aws_util.aws_utils import ensure_aws_access
from .create.project.create_project_cmd import create_project
from .create.project.create_project_request import CreateProjectRequest
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
    parser.add_argument("--unsecured", action="store_true", help="Do not put on HTTPS protocol and CFN.")
    args = parser.parse_args()

    project_name: str = args.name
    static_site_domain: str = args.static_site
    sub_domain: Union[str, None] = args.sub_domain if len(args.sub_domain) > 0 else None
    dry_run: bool = args.dry_run
    unsecured: bool = args.unsecured
    should_create_template: bool = True
    should_create_infrastructure: bool = False

    kix.info(f"Project Name: {project_name}")
    kix.info(f"Domain Name: {static_site_domain}")
    kix.info(f"Sub Domain: {sub_domain}")
    kix.info(f"Dry-run: {str(dry_run)}")
    kix.info(f"Creating Template Site: {str(should_create_template)}")

    user_target = 1000
    os.setgid(user_target)
    os.setuid(user_target)
    kix.info(f"Setting UID and GID to {user_target} to relax file permissions.")

    # If local only, do not need to go past this point.
    create_local_resources(project_name)

    # Create template site.
    project_request = CreateProjectRequest()
    create_project(project_request)

    # AWS Validation.
    service_model: InfrastructureServiceModel = ensure_aws_access()

    if static_site_domain is not None:
        request = CreateStaticSiteRequest(project_name, static_site_domain, sub_domain, with_https=not unsecured)
        static_site_svc_model = create_static_site(request)
        service_model.append(static_site_svc_model)

        kix.info("Bootstrapping CDK")
        bootstrap = f"cdk bootstrap aws://{service_model.aws_account_id.value}/us-east-1"
        kix.info(f"Bootstrap Command: {bootstrap}")
        os.system(bootstrap)
        should_create_infrastructure = True

    if should_create_infrastructure:
        create_infrastructure(service_model, dry_run)


def create_local_resources(project_name: str):
    path = project_name

    # Check if the directory already exists.
    if os.path.exists(path):
        message = f"Cannot create project {project_name}. The directory {project_name} already exists."
        kix.error(message)
        raise IsADirectoryError(message)

    # It doesn't exist, so we can try to make the project here.
    os.mkdir(path)
    os.chdir(path)
    kix.info(f"Project path changed to: {os.getcwd()}")

    # Create a project definition and save it locally.
    project_definition_model = ProjectDefinitionModel()
    project_definition_model.model_path = os.getcwd()
    project_definition_model.project_name = project_name
    project_definition_model.save_to_local()


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
