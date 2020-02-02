import os
from shutil import rmtree

OUTPUT_DIR = "output"


def redirect_output() -> str:
    if os.path.exists(OUTPUT_DIR):
        rmtree(OUTPUT_DIR)

    os.mkdir(OUTPUT_DIR)
    os.chdir(OUTPUT_DIR)
    return os.getcwd()


def clear_output(original_dir: str):
    os.chdir(original_dir)
    if os.path.exists(OUTPUT_DIR):
        rmtree(OUTPUT_DIR)
