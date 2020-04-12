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

    table_name: str = "items"
    api_domain_name = f"api2.{domain}"

    # Add Authentication ===============================================================================================

    user_pool = aws_cognito.UserPool(
        scope=stack,
        id="UserPool",
        auto_verify=aws_cognito.AutoVerifiedAttrs(email=True)
    )

    aws_cognito.UserPoolClient(
        scope=stack,
        user_pool=user_pool,
        id="AuthClientWeb",
        generate_secret=False
    )

    id_pool = aws_cognito.CfnIdentityPool(
        scope=stack,
        id="IdentityPool",
        allow_unauthenticated_identities=True
    )

    # Add CRUD DataStore  =====================================================================

    table_partition_key = aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING)
    table = aws_dynamodb.Table(
        scope=stack,
        id="CrudTable",
        table_name=table_name,
        partition_key=table_partition_key,
        removal_policy=core.RemovalPolicy.DESTROY)

    # Add CRUD API =====================================================================================================

    certificate = create_api_certificate(stack, api_domain_name, stack.zone)
    domain_options = aws_apigateway.DomainNameOptions(domain_name=api_domain_name, certificate=certificate)
    stage_options = aws_apigateway.StageOptions(
        throttling_rate_limit=10,
        throttling_burst_limit=100
    )

    api = aws_apigateway.RestApi(
        scope=stack,
        id="CrudApiGW",
        rest_api_name="Crud API Zinc",
        domain_name=domain_options,
        deploy_options=stage_options
    )

    authorizer = aws_apigateway.CfnAuthorizer(
        scope=stack,
        name="ApiGWAuthorizer",
        id="ApiGWAuthorizer",
        type="COGNITO_USER_POOLS",
        provider_arns=[user_pool.user_pool_arn],
        rest_api_id=api.rest_api_id,
        identity_source="method.request.header.Authorization"
    )

    kix.info("Routing A-Record Alias")
    a_record_target = aws_route53.RecordTarget.from_alias(aws_route53_targets.ApiGateway(api))
    aws_route53.ARecord(
        stack, "CrudApiAliasRecord",
        zone=stack.zone,
        target=a_record_target,
        record_name=api_domain_name)

    create_api(api_handler="lambda_handler.get_handler",
               api_name="GetItem",
               api_method="GET",
               api_path="crudget",
               stack=stack, table=table, api=api, authorizer=authorizer)

    create_api(api_handler="lambda_handler.post_handler",
               api_name="PostItem",
               api_method="POST",
               api_path="crudpost",
               stack=stack, table=table, api=api, authorizer=authorizer)

    core.CfnOutput(stack, 'CrudApiEndpointURL', value=api.url)


def create_api(
        api_handler: str,
        api_name: str,
        api_method: str,
        api_path: str,
        stack: CDKMasterStack,
        table: aws_dynamodb.Table,
        api: aws_apigateway.RestApi,
        authorizer: aws_apigateway.CfnAuthorizer
):

    module_path = os.path.dirname(__file__)
    lambda_path = os.path.join(module_path, "lambda")
    api_function = aws_lambda.Function(
        scope=stack,
        id=f"{api_name}Function",
        handler=api_handler,
        runtime=aws_lambda.Runtime.PYTHON_3_7,
        environment={
            "TABLE_NAME": table.table_name
        },
        code=aws_lambda.Code.asset(lambda_path),
    )

    api_entity = api.root.add_resource(api_path)
    api_lambda_integration = aws_apigateway.LambdaIntegration(
        api_function,
        proxy=False,
        integration_responses=[get_integration_response()])

    get_api = api_entity.add_method(
        api_method,
        api_lambda_integration,
        method_responses=[get_method_response()],
        authorization_type=aws_apigateway.AuthorizationType.COGNITO
    )

    get_api.node.find_child("Resource").add_property_override('AuthorizerId', authorizer.ref)
    add_cors_options(api_entity)
    table.grant_full_access(api_function)


def create_api_certificate(stack: core.Stack, domain: str, zone: aws_route53.HostedZone):
    kix.info("Creating Certificate")
    cert = aws_certificatemanager.DnsValidatedCertificate(
        stack, f"CrudApiCertificate",
        domain_name=domain,
        hosted_zone=zone)
    core.CfnOutput(stack, 'CrudApiCertificateArn', value=cert.certificate_arn)
    return cert


def add_cors_options(api_gateway_resource):
    api_gateway_resource.add_method(
        'OPTIONS',
        aws_apigateway.MockIntegration(
            integration_responses=[get_options_integration_response()],
            passthrough_behavior=aws_apigateway.PassthroughBehavior.WHEN_NO_MATCH,
            request_templates={"application/json": "{\"statusCode\":200}"}),
        method_responses=[get_options_method_response()])


def get_integration_response():
    integration_response = aws_apigateway.IntegrationResponse(
        status_code="200",
        response_parameters={'method.response.header.Access-Control-Allow-Origin': "'*'"})
    return integration_response


def get_method_response():
    method_response = aws_apigateway.MethodResponse(
        status_code="200",
        response_parameters={'method.response.header.Access-Control-Allow-Origin': True})
    return method_response


def get_options_integration_response():
    integration_response = aws_apigateway.IntegrationResponse(
        status_code="200",
        response_parameters={
            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
            'method.response.header.Access-Control-Allow-Origin': "'*'",
            'method.response.header.Access-Control-Allow-Methods': "'GET,OPTIONS'"
        }
    )
    return integration_response


def get_options_method_response():
    method_response = aws_apigateway.MethodResponse(
        status_code="200",
        response_parameters={
            'method.response.header.Access-Control-Allow-Headers': True,
            'method.response.header.Access-Control-Allow-Methods': True,
            'method.response.header.Access-Control-Allow-Origin': True,
        }
    )
    return method_response
