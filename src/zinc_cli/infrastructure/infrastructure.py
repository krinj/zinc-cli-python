#!/usr/bin/env python3
from aws_cdk import core
from models.infrastructure_service_model import InfrastructureServiceModel
from services.contact_api.cdk_contact_api_stack import add_contact_api
from services.master_stack import CDKMasterStack
from services.static_site.cdk_static_site_stack import add_static_site


def build(m: InfrastructureServiceModel):

    # This is the build definition.
    app = core.App()

    # Prepare the environment variables.
    env = {"account": m.aws_account_id.value, "region": m.aws_region.value}
    stack_id = f"{m.project_name.value}-zinc-stack"

    # Create the master stack.
    master_stack = CDKMasterStack(app, stack_id, domain=m.domain_name.value, env=env)

    # Static site.
    if m.create_static_site.value:
        add_static_site(master_stack, domain=m.domain_name.value, bucket_name=m.static_site_bucket_name.value)

    # Contact Form API.
    if m.create_contact_api.value:
        add_contact_api(master_stack, domain=m.domain_name.value)

    # Synthesize the application.
    app.synth()


def main():
    print("Deploying CDK Stack")
    # Load the service model from the environment.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    service_model.load_from_environ()
    build(service_model)


if __name__ == "__main__":
    main()
