# This function creates a project the same way like a React project.
import argparse
import os

from zinc_cli.commands.create.domain.domain_manager import user_owns_domain
from zinc_cli.models.project_definition.project_definition_model import ProjectDefinitionModel
from zinc_cli.service.create_project_table_ddb import create_project_table_ddb


def invoke():
    print("Creating Project...")

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, required=True, help="Name of the new project.")
    parser.add_argument("-s", "--static-site", type=str, help="Bootstrap a static site at the domain.")
    args = parser.parse_args()

    project_name = args.name
    static_site_domain = args.static_site
    print("p: " + project_name)
    print("s: " + static_site_domain)
    user_owns_domain(static_site_domain)
    create_project(project_name)


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


def create_infrastructure(project_name: str):
    module_path = os.path.dirname(__file__)
    current_path = os.getcwd()
    infrastructure_path = os.path.join(module_path, "..", "infrastructure")
    os.chdir(infrastructure_path)
    print(f"Changed Directory to {infrastructure_path} to execute CDK.")
    result = os.system(f"PROJECT_NAME={project_name} cdk deploy --require-approval never")
    print(f"Executed Result: {result}")
    os.chdir(current_path)
    print(f"Changed Directory back to {current_path}.")
