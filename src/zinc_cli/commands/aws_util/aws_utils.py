import boto3
from zinc_cli.infrastructure.models.infrastructure_service_model import InfrastructureServiceModel


def ensure_aws_access():
    # Ensure the account credentials.
    service_model: InfrastructureServiceModel = InfrastructureServiceModel()
    try:
        account = boto3.client('sts').get_caller_identity().get('Account')
        my_session = boto3.session.Session()
        my_region = my_session.region_name

        if account is None:
            raise Exception("AWS Account is not configured")

        if my_region is None:
            raise Exception("AWS Region is not configured")

        print(f"Using AWS Account: {account}")
        print(f"Using AWS Region: {my_region}")
        print("If you would like to change accounts/regions, configure the default aws profile with 'aws configure'.")
        service_model.aws_account_id.set(account)
        service_model.aws_region.set(my_region)
        return service_model

    except Exception as e:
        print("Error: ", str(e))
        raise Exception("Failed to get AWS credentials. Have you installed awscli and run 'aws configure'?")
