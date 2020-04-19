import kix
from aws_cdk import (
    core,
    aws_lambda,
    aws_apigateway,
    aws_dynamodb,
    aws_certificatemanager, aws_route53, aws_route53_targets, aws_cognito)
import os

from services.master_stack import CDKMasterStack


def add_crud_api(stack: CDKMasterStack, project_name: str, domain: str):

    # Add Authentication ===============================================================================================

    # id_pool = aws_cognito.CfnIdentityPool(
    #     scope=stack,
    #     id="IdentityPool",
    #     allow_unauthenticated_identities=True
    # )

    # Add CRUD API =====================================================================================================
    module_path = os.path.dirname(__file__)
    lambda_path = os.path.join(module_path, "lambda")
    stack.add_crud_api(api_path="item", lambda_handler_path=lambda_path, get_access_auth=False, edit_access_auth=True)
