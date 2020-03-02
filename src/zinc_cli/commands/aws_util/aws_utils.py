import os
import boto3
import kix
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def create_aws_service_model():

    # Ensure the account credentials, then return the service model.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()

    try:
        account = boto3.client('sts').get_caller_identity().get('Account')
        my_region = "us-east-1"  # All accounts created in us-east-1.

        if account is None:
            raise Exception("AWS Account is not configured")

        if my_region is None:
            raise Exception("AWS Region is not configured")

        kix.info(f"Using AWS Account: {account}")
        kix.info(f"Using AWS Region: {my_region}")
        kix.info("If you would like to change accounts/regions, configure the default aws profile with 'aws configure'.")

        service_model.aws_account_id.set(account)
        service_model.aws_region.set(my_region)

        return service_model

    except Exception as e:
        kix.error("Error: ", str(e))
        raise Exception("Failed to get AWS credentials. Have you installed awscli and run 'aws configure'?")


def bootstrap_cdk(account_id: str, region: str):
    kix.info("Bootstrapping CDK")
    bootstrap = f"cdk bootstrap aws://{account_id}/{region}"
    kix.info(f"Bootstrap Command: {bootstrap}")
    os.system(bootstrap)
