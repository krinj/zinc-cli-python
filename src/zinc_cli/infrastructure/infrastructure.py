#!/usr/bin/env python3
from aws_cdk import core
from models.infrastructure_service_model import InfrastructureServiceModel
from services.contact_api.cdk_contact_api_stack import add_contact_api
from services.crud_api.cdk_crud_stack import add_crud_api
from services.master_stack import CDKMasterStack
from services.static_site.cdk_static_site_stack import add_static_site


def build(m: InfrastructureServiceModel):

    # This is the build definition.
    app = core.App()

    # Prepare the environment variables.
    env = {"account": m.aws_account_id.value, "region": m.aws_region.value}
    stack_id = f"{m.project_name.value}-pxw-stack"

    # Create the master stack.
    master_stack = CDKMasterStack(app, stack_id, domain=m.domain_name.value, env=env)

    # Static site.
    if m.create_static_site.value:
        add_static_site(master_stack, domain=m.domain_name.value, bucket_name=m.static_site_bucket_name.value)
        admin_domain = f"admin.{m.domain_name.value}"
        admin_bucket = f"admin.{m.static_site_bucket_name.value}"
        add_static_site(master_stack, domain=admin_domain, bucket_name=admin_bucket, prefix="Admin")

    # Contact Form API.
    if m.create_contact_api.value:
        add_contact_api(master_stack,
                        project_name=m.project_name.value,
                        domain=m.domain_name.value,
                        forwarding_email=m.forwarding_email.value)

    # Crud API.
    if m.create_crud_api.value:
        add_crud_api(
            master_stack,
            project_name=m.project_name.value,
            domain=m.domain_name.value)

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
