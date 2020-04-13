# Running this script will copy the contents of 'util_src' to all lambda service packages.
import os
import shutil

import kix


def main():

    module_directory = os.path.dirname(__file__)
    service_directory = os.path.join(os.path.dirname(__file__), "..")
    service_folders = os.listdir(service_directory)

    for folder_name in service_folders:
        service_path = os.path.join(service_directory, folder_name)
        if os.path.abspath(service_path) == os.path.abspath(module_directory):
            kix.warning(f"Skipping {service_path} because it is this utils directory.")
            continue

        if not os.path.isdir(service_path):
            kix.warning(f"Skipping {service_path} because it is not a directory.")
            continue

        lambda_path = os.path.join(service_path, "lambda")
        if not os.path.exists(lambda_path):
            kix.warning(f"Skipping {service_path} because it does not contain a Lambda directory.")
            continue

        copy_util_files(lambda_path)


def copy_util_files(path: str):
    kix.info(f"Copying util files into {path}")
    target_dir = os.path.join(path, "util_src")

    # Clear out the directory if it already exists.
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)

    # Create it again.
    os.mkdir(target_dir)

    # Use shell to copy all the files in.
    os.system(f"cp -r ./util_src/* {target_dir}")


if __name__ == "__main__":
    main()
