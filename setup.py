# -*- coding: utf-8 -*-
import json
import os
from shutil import rmtree
import setuptools

# ======================================================================================================================
# Fill in this information for each package.
# ======================================================================================================================

# Edit these.
AUTHOR = "Jakrin Juangbhanich"
EMAIL = "juangbhanich.k@gmail.com"
DESCRIPTION = "Package Description."
REPO = "https://github.com/krinj"

# Project Defaults.
PACKAGE_SRC = "src"
SCRIPTS_SRC = "scripts"
SCRIPTS_FULL_PATH = os.path.join(PACKAGE_SRC, SCRIPTS_SRC)

# ======================================================================================================================
# Discover the core package.
# ======================================================================================================================

# Work out the sources package.
src_paths = os.listdir(PACKAGE_SRC)
src_paths.remove("__pycache__")  # Make sure we don't include this by accident.
src_paths.remove("__init__.py")  # Make sure we don't include this by accident.
src_paths.remove(SCRIPTS_SRC)  # Also remove the scripts directory.

if len(src_paths) != 1:
    raise Exception(f"Failed to build: Source directory '{PACKAGE_SRC}' must contain exactly one Python package. "
                    f"Instead, it contains {len(src_paths)}: {src_paths}")

PACKAGE_NAME = src_paths[0]
PACKAGE_PATH = os.path.join(PACKAGE_SRC, PACKAGE_NAME)

print(f"Package Name Discovered: {PACKAGE_NAME}")

# ======================================================================================================================
# Automatic Package Setup Script.
# ======================================================================================================================

# Bump the version.
with open("version", "r") as f:
    current_version = f.readline()
    versions = current_version.split(".")
    versions[-1] = str(int(versions[-1]) + 1)
    new_version = ".".join(versions)

with open("version", "w") as f:
    f.write(new_version)

print("Bumping Version Number: {} -> {}".format(current_version, new_version))

with open("version", "r") as f:
    VERSION = f.readline()


def copy_version_to_package(path):
    """ Copy the single source of truth version number into the package as well. """
    init_file = os.path.join(path, "__init__.py")
    with open(init_file, "r") as original_file:
        lines = original_file.readlines()

    with open(init_file, "w") as new_file:
        for line in lines:
            if "__version__" not in line:
                new_file.write(line)
            else:
                new_file.write("__version__ = \"{}\"\n".format(VERSION))


copy_version_to_package(PACKAGE_PATH)

with open("long_description.md", "r") as f:
    long_description = f.read()

scripts = [os.path.join(SCRIPTS_FULL_PATH, f) for f in os.listdir(SCRIPTS_FULL_PATH)]
print("Scripts Discovered: " + str(scripts))

packages = setuptools.find_packages(PACKAGE_SRC)
print(f"Packages Discovered: {packages}")

with open("requirements.txt", "r") as f:
    requirement_packages = [line.strip('\n') for line in f.readlines()]
print(f"Requirements: {requirement_packages}")

setuptools.setup(
    author=AUTHOR,
    author_email=EMAIL,
    name=PACKAGE_NAME,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=VERSION,
    url=REPO,
    packages=packages,
    package_dir={PACKAGE_NAME: PACKAGE_PATH},
    install_requires=requirement_packages,
    scripts=scripts,
    classifiers=[
        "Programming Language :: Python :: 3.7"
    ],
    package_data={PACKAGE_NAME: ['infrastructure/*.json']}
)


def load_credentials():
    CREDENTIALS_PATH = "pypi_credentials.json"
    if not os.path.exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, "w") as f:
            json.dump({"user": "username", "pass": "password"}, f)
        print(f"No credentials detected. Please enter your credentials in: {CREDENTIALS_PATH}")
        exit(0)

    with open(CREDENTIALS_PATH, "r") as f:
        credentials = json.load(f)

    return credentials["user"], credentials["pass"]


def upload_distribution():
    repo_user, repo_pass = load_credentials()
    command = f"twine upload -u {repo_user} -p {repo_pass} dist/*"
    os.system(command)


upload_distribution()


def remove_artifacts(path):
    if os.path.exists(path):
        rmtree(path)
        print(f"Removed: {path}")


remove_artifacts("build")
remove_artifacts("dist")
remove_artifacts(f"{PACKAGE_NAME}.egg-info")


# # ===================================================================================================
# # Upload to PyPI. Get the user and password from the environment.
# # ===================================================================================================
#
# key_repo_user = "REPO_USER"
# key_repo_pass = "REPO_PASS"
#
# if key_repo_user in os.environ and key_repo_pass in os.environ:
#     repo_user = os.environ[key_repo_user]
#     repo_pass = os.environ[key_repo_pass]
#
#     with open("upload_to_pypi.sh", 'w') as f:
#         f.write('#!/usr/bin/env bash\n')
#         f.write('pip install twine\n')
#         f.write('twine upload -u {} -p {} dist/*\n'.format(repo_user, repo_pass))
# else:
#     raise Exception(f"Environment variables for uploading to PyPI not found: {key_repo_user} and {key_repo_pass}.")
