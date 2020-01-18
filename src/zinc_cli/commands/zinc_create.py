# This function creates a project the same way like a React project.
import os


def invoke():
    print("Creating Project...")
    create_project("new_project")
    pass


def create_project(project_name: str):
    path = project_name

    # Check if the directory already exists.
    if os.path.exists(path):
        raise IsADirectoryError(f"Cannot create project {project_name}. "
                                f"The directory {project_name} already exists.")

    # It doesn't exist, so we can try to make the project here.
    os.mkdir(path)

