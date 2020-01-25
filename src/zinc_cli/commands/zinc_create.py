# This function creates a project the same way like a React project.
import argparse
import os

import boto3

from zinc_cli.infrastructure.app import build
from zinc_cli.commands.create.domain.domain_manager import DomainManager
from zinc_cli.models.project_definition.project_definition_model import ProjectDefinitionModel
from zinc_cli.service.create_project_table_ddb import create_project_table_ddb


def invoke():
    print("Creating Project...")

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, required=True, help="Name of the new project.")
    parser.add_argument("-s", "--static-site", type=str, help="Bootstrap a static site at the domain.")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Do not publish to actual AWS.")
    args = parser.parse_args()

    project_name = args.name
    static_site_domain = args.static_site
    dry_run = args.dry_run

    print("p: " + project_name)
    print("s: " + static_site_domain)
    print("dry run: " + str(dry_run))
    # create_project(project_name)

    if static_site_domain is not None:
        create_static_site(project_name, static_site_domain, dry_run)


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


def create_static_site(project_name: str, domain_name: str, dry_run: bool):
    print(f"Creating Static Site: {domain_name}")

    # Ensure AWS Access.
    aws_has_access, aws_account, aws_region = ensure_aws_access()
    if not aws_has_access:
        exit(0)

    # Ensure the domain.
    if not DomainManager.validate(domain_name):
        raise Exception(f"Not a valid domain name: {domain_name}")

    if not DomainManager.user_owns_domain(domain_name):
        raise Exception(f"You do not own this domain: {domain_name}. Please register it on your AWS account.")

    # Deploy the stack.
    create_infrastructure(project_name, domain_name, aws_account, aws_region, dry_run)


def ensure_aws_access():
    # Ensure the account credentials.
    try:
        account = boto3.client('sts').get_caller_identity().get('Account')
        my_session = boto3.session.Session()
        my_region = my_session.region_name

        if account is None:
            raise Exception("AWS Account is not configured")

        if my_region is None:
            raise Exception("AWS Region is not configured")

        print(f"Using AWS Account: {account}")
        print(f"Using AWS Region: {my_region}")
        print("If you would like to change accounts/regions, configure the default aws profile with 'aws configure'.")
        return True, account, my_region

    except Exception as e:
        print("Error: ", str(e))
        print("Failed to get AWS credentials. Have you installed awscli and run 'aws configure'?")

    return False, None, None


def create_infrastructure(project_name: str, static_domain: str, aws_account: str, aws_region: str, dry_run: bool):
    module_path = os.path.dirname(__file__)
    current_path = os.getcwd()
    infrastructure_path = os.path.join(module_path, "..", "infrastructure")
    os.chdir(infrastructure_path)
    print(f"Changed Directory to {infrastructure_path} to execute CDK.")

    env_vars = f"ZC_PROJECT_NAME={project_name} " \
               f"ZC_SITE_DOMAIN={static_domain} " \
               f"ZC_AWS_ACCOUNT={aws_account} " \
               f"ZC_AWS_REGION={aws_region}"

    deploy_command = "deploy" if dry_run is False else "synth"
    result = os.system(f"{env_vars} cdk {deploy_command} --require-approval never")
    print(f"Executed Result: {result}")
    os.chdir(current_path)
    print(f"Changed Directory back to {current_path}.")
