#!/usr/bin/env python3
import argparse

import kix
from aws_cdk import core
from aws_cdk.cx_api import CloudAssembly

import os

from models.infrastructure_service_model import InfrastructureServiceModel
from services.bookings.cdk_bookings_stack import CDKBookingsStack
from services.static_site.cdk_static_site_stack import CDKStaticSiteStack


def build(service_model: InfrastructureServiceModel):

    # This is the build definition.
    app = core.App()

    # Create the stacks.
    # CDKBookingsStack(app, f"ZincBookings-{project_id}", project_id)

    # Static site: Region must be us-east-1 for Route53 and CDN.
    env = {"account": service_model.aws_account_id.value, "region": "us-east-1"}
    static_stack_id = f"{service_model.project_name.value}-zinc-static-site"
    CDKStaticSiteStack(app, static_stack_id, service_model.project_name.value,
                       root_domain=service_model.static_site_root_domain.value,
                       sub_domain=service_model.static_site_sub_domain.value,
                       env=env)

    # Synthesize the application.
    app.synth()


def main():
    print("Deploying CDK Stack")

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--project-name", type=str, help="Name of the new project.")
    # parser.add_argument("--site-domain", type=str, help="Bootstrap a static site at the domain.")
    # parser.add_argument("--aws-account", type=str, help="Bootstrap a static site at the domain.")
    # parser.add_argument("--aws-region", type=str, help="Bootstrap a static site at the domain.")
    # args = parser.parse_args()

    # Load the service model from the environment.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    service_model.load_from_environ()
    build(service_model)


if __name__ == "__main__":
    main()
