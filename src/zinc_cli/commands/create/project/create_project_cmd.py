import json
import shutil
import subprocess

import kix

from.create_project_request import CreateProjectRequest
import os


def create_project(request: CreateProjectRequest):
    # Download the template into the directory.

    CLONE_REPO = "https://github.com/krinj/zinc-react-template.git"
    FOLDER_NAME = "zinc-react-template"
    DESTINATION = "site-template"

    print(f"Creating projeting in {os.getcwd()}")

    # Clone the repo.
    kix.info(f"Cloning template site from: {CLONE_REPO}")
    subprocess.call(["git", "clone", CLONE_REPO])

    # Copy the template folder.
    app_folder_path = os.path.join(FOLDER_NAME, "app")
    shutil.copytree(app_folder_path, DESTINATION)
    kix.info(f"Copied template source from {app_folder_path} to {DESTINATION}")

    # Delete source.
    shutil.rmtree(FOLDER_NAME)
    kix.info(f"Source removed: {FOLDER_NAME}")

    # Replace the deployment script.
    package_json_path = os.path.join(DESTINATION, "package.json")
    with open(package_json_path, "r") as f:
        current_package_json = json.load(f)

    # Inject the deployment script.
    s3_bucket = "BUCKET-NAME-PLACEHOLDER"
    deploy_script = f"aws s3 sync build/ s3://{s3_bucket} --acl public-read"
    current_package_json["scripts"]["deploy"] = deploy_script
    with open(package_json_path, "w") as f:
        json.dump(current_package_json, f, indent=2)

    kix.info("package.json updated with deployment script")
