#!/usr/bin/env python3
import argparse

from aws_cdk import core
from aws_cdk.cx_api import CloudAssembly

from zinc_cli.infrastructure.services.bookings.cdk_bookings_stack import CDKBookingsStack
import os

from zinc_cli.infrastructure.services.static_site.cdk_static_site_stack import CDKStaticSiteStack


def build(project_name: str, site_domain: str, aws_account: str, aws_region: str) -> CloudAssembly:

    # This is the build definition.
    app = core.App()
    project_id = "my_new_project"

    # Use environment vars to load configuration.
    if "PROJECT_NAME" in os.environ:
        project_id = os.environ["PROJECT_NAME"]
        print(f"Project Name Override: {project_id}")

    # Create the stacks.
    # CDKBookingsStack(app, f"ZincBookings-{project_id}", project_id)

    # Static site: Region must be us-east-1 for Route53 and CDN.
    env = {"account": aws_account, "region": "us-east-1"}
    static_stack_id = f"ZStaticSite-{project_name}"
    CDKStaticSiteStack(app, static_stack_id, project_name, domain_name=site_domain, env=env)

    # Synthesize the application.
    result = app.synth()
    return result


def main():
    print("Deploying CDK Stack")

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--project-name", type=str, help="Name of the new project.")
    # parser.add_argument("--site-domain", type=str, help="Bootstrap a static site at the domain.")
    # parser.add_argument("--aws-account", type=str, help="Bootstrap a static site at the domain.")
    # parser.add_argument("--aws-region", type=str, help="Bootstrap a static site at the domain.")
    # args = parser.parse_args()

    build(
        os.environ["ZC_PROJECT_NAME"],
        os.environ["ZC_SITE_DOMAIN"],
        os.environ["ZC_AWS_ACCOUNT"],
        os.environ["ZC_AWS_REGION"])


if __name__ == "__main__":
    main()
