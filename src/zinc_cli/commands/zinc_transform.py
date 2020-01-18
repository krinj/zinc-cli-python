import argparse
import os
from typing import TextIO

TEMPLATE_TOKEN = "<INSERT_TOKEN>"
INDENT_CHAR = "    "


def content_template():
    x = """import ZincContentInterface from "./zincContentInterface";
    
    class ZincContent extends ZincContentInterface {
        constructor () {
            super();
            <INSERT_TOKEN>
        }
    }
    
    export default ZincContent
    """
    return x


def invoke():
    print("Creating Project...")

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--template_path", type=str, required=True, help="Path to the front-end template to transform into.")
    args = parser.parse_args()

    template_path = args.template_path
    print("tp: " + template_path)
    transform_project(template_path)


def transform_project(template_path: str = ""):
    # Transforms a project into a TypeScript object so a front-end can import it.
    path = os.path.join(template_path, "zinc")
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    path = os.path.join(path, "zincContent.ts")

    template = content_template()

    with open(path, "w") as file:

        indent_level = 0

        for template_line in template.split("\n"):
            template_line = template_line.strip()

            if TEMPLATE_TOKEN in template_line:
                write_content(file, indent_level)
            else:
                indent_level = process_template_line(file, indent_level, template_line)


def process_template_line(file: TextIO, indent_level: int, template_line: str):

    if "}" in template_line:
        indent_level -= 1

    file.write(get_indent(indent_level))
    file.write(template_line + "\n")

    if "{" in template_line:
        indent_level += 1

    return indent_level


def get_indent(level: int):
    return level * INDENT_CHAR


def write_content(file: TextIO, indent_level: int):
    for i in range(3):
        file.write(get_indent(indent_level))
        file.write("this.addBody('This is injected content!');")
        file.write("\n")
