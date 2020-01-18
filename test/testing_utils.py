import os
from shutil import rmtree

OUTPUT_DIR = "output"


def redirect_output():
    if os.path.exists(OUTPUT_DIR):
        rmtree(OUTPUT_DIR)

    os.mkdir(OUTPUT_DIR)
    os.chdir(OUTPUT_DIR)
