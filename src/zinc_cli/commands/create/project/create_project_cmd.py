import json
import shutil
import subprocess
import os
import kix

from.create_project_request import CreateProjectRequest


def create_project(request: CreateProjectRequest):
    # Download the template into the directory.

    clone_repo = "https://github.com/krinj/zinc-react-template.git"
    content_folder_src = "zinc-react-template"
    content_folder_dst = "site"
    project_path = request.project_name
    original_path = os.getcwd()

    _create_local_resources(request.project_name, project_path)
    _clone_template_site(clone_repo, content_folder_dst, content_folder_src)
    _inject_deployment_script(content_folder_dst, request)
    _install_project_modules(content_folder_dst)

    if request.dry_run:
        kix.info("Dry run: Removing all local resources.")
        os.chdir(original_path)
        shutil.rmtree(project_path)


def _inject_deployment_script(destination: str, request: CreateProjectRequest):
    # Replace the deployment script.
    package_json_path = os.path.join(destination, "package.json")
    with open(package_json_path, "r") as f:
        current_package_json = json.load(f)

    # Inject the deployment script.
    deploy_script = f"aws s3 sync build/ s3://{request.bucket_name} --acl public-read"
    current_package_json["scripts"]["deploy"] = deploy_script
    with open(package_json_path, "w") as f:
        json.dump(current_package_json, f, indent=2)
    kix.info("package.json updated with deployment script")

    # Inject the API endpoint.
    api_endpoint = f"https://api.{request.domain_name}"


def _install_project_modules(destination: str):
    current_dir = os.getcwd()
    os.chdir(destination)
    subprocess.call(["yarn", "install"])
    os.chdir(current_dir)


def _clone_template_site(repo_address: str, destination: str, source_path: str):
    kix.info(f"Creating project in {os.getcwd()}")

    # Clone the repo.
    kix.info(f"Cloning template site from: {repo_address}")
    subprocess.call(["git", "clone", repo_address])

    # Copy the template folder.
    app_folder_path = os.path.join(source_path, "app")
    shutil.copytree(app_folder_path, destination)
    kix.info(f"Copied template source from {app_folder_path} to {destination}")

    # Delete source.
    shutil.rmtree(source_path)
    kix.info(f"Source removed: {source_path}")


def _create_local_resources(project_name: str, path: str):
    # Check if the directory already exists.
    if os.path.exists(path):
        message = f"Cannot create project {project_name}. The directory {path} already exists."
        kix.error(message)
        raise IsADirectoryError(message)

    # It doesn't exist, so we can try to make the project here.
    os.mkdir(path)
    os.chdir(path)
    kix.info(f"Project path changed to: {os.getcwd()}")
