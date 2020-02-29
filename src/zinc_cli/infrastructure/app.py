#!/usr/bin/env python3
from aws_cdk import core
from models.infrastructure_service_model import InfrastructureServiceModel
from services.contact_api.cdk_contact_api_stack import CDKContactApiStack
from services.static_site.cdk_static_site_stack import CDKStaticSiteStack
from services.crud_api.cdk_crud_stack import CDKCrudApiStack


def build(service_model: InfrastructureServiceModel):

    # This is the build definition.
    app = core.App()

    # Static site: Region must be us-east-1 for Route53 and CDN.
    if service_model.create_static_site.value:
        env = {"account": service_model.aws_account_id.value, "region": "us-east-1"}
        static_stack_id = f"{service_model.project_name.value}-zinc-static-site"
        with_https: bool = service_model.with_https.value
        CDKStaticSiteStack(
            app, static_stack_id, service_model.project_name.value,
            root_domain=service_model.static_site_root_domain.value,
            sub_domain=service_model.static_site_sub_domain.value,
            with_https=with_https,
            env=env)

    # Lambda API Stack.
    if service_model.create_crud_api.value:
        env = {"account": service_model.aws_account_id.value, "region": "us-east-1"}
        crud_stack_id = f"{service_model.project_name.value}-zinc-crud-api"
        CDKCrudApiStack(app, crud_stack_id, domain="zinccli.com", env=env)

    # Lambda API Stack.
    if service_model.create_contact_api.value:
        env = {"account": service_model.aws_account_id.value, "region": "us-east-1"}
        crud_stack_id = f"{service_model.project_name.value}-zinc-contact-api"
        CDKContactApiStack(app, crud_stack_id, domain="zinccli.com", env=env)

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
