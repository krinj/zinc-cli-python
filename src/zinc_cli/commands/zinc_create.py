# This function creates a project the same way like a React project.
import argparse
import os

from zinc_cli.models.project_definition.project_definition_model import ProjectDefinitionModel
from zinc_cli.service.create_project_table_ddb import create_project_table_ddb


def invoke():
    print("Creating Project...")

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, required=True, help="Name of the new project.")
    args = parser.parse_args()

    project_name = args.name
    print("p: " + project_name)
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
    project_definition_model.create_table()
    project_definition_model.save_to_cloud()
