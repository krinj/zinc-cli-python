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

    module_path = os.path.dirname(__file__)
    lambda_path = os.path.join(module_path, "lambda")
    table_name: str = "items"
    api_path: str = "crud"
    api_domain_name = f"api2.{domain}"
    table_partition_key = aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING)

    # Add Authentication ===============================================================================================

    user_pool = aws_cognito.UserPool(
        scope=stack,
        id="UserPool",
        auto_verify=aws_cognito.AutoVerifiedAttrs(email=True)
    )

    app_client = aws_cognito.UserPoolClient(
        scope=stack,
        user_pool=user_pool,
        id="AuthClientWeb",
        generate_secret=False
    )

    # Add CRUD API =====================================================================================================

    table = aws_dynamodb.Table(
        scope=stack,
        id="CrudTable",
        table_name=table_name,
        partition_key=table_partition_key,
        removal_policy=core.RemovalPolicy.DESTROY)

    api_function = aws_lambda.Function(
        scope=stack,
        id="ApiCrudFunction",
        handler='lambda_handler.handler',
        runtime=aws_lambda.Runtime.PYTHON_3_7,
        environment={
        },
        code=aws_lambda.Code.asset(lambda_path),
    )

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

    api_entity = api.root.add_resource(api_path)
    api_lambda_integration = aws_apigateway.LambdaIntegration(
        api_function,
        proxy=False,
        integration_responses=[get_integration_response()])

    get_api = api_entity.add_method(
        'GET',
        api_lambda_integration,
        method_responses=[get_method_response()],
        authorization_type=aws_apigateway.AuthorizationType.COGNITO
    )

    get_api.node.find_child("Resource").add_property_override('AuthorizerId', authorizer.ref)

    # get_api.node.add_dependency(authorizer)
    add_cors_options(api_entity)
    table.grant_full_access(api_function)
    core.CfnOutput(stack, 'CrudApiEndpointURL', value=api.url)


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
