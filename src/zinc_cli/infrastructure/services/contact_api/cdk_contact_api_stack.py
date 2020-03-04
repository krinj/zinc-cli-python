import kix
from aws_cdk import (
    core,
    aws_lambda,
    aws_apigateway,
    aws_certificatemanager, aws_route53, aws_route53_targets, aws_iam)
import os

from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.custom_resources import AwsCustomResource, AwsSdkCall
from services.master_stack import CDKMasterStack


def add_contact_api(stack: CDKMasterStack, project_name: str, domain: str, forwarding_email: str):

    module_path = os.path.dirname(__file__)
    lambda_path = os.path.join(module_path, "lambda")
    api_domain_name = f"api.{domain}"
    api_path = "contact"

    base_lambda = aws_lambda.Function(
        stack, 'ContactFormLambda',
        handler='lambda_handler.handler',
        runtime=aws_lambda.Runtime.PYTHON_3_7,
        environment={
            "TARGET_EMAIL": forwarding_email,
            "SENDER_EMAIL": f"contact@{domain}",
            "SENDER_NAME": f"{project_name.capitalize()} Contact Form"
        },
        code=aws_lambda.Code.asset(lambda_path),
    )

    base_lambda.add_to_role_policy(aws_iam.PolicyStatement(
        effect=aws_iam.Effect.ALLOW,
        resources=["*"],
        actions=["ses:SendEmail", "ses:SendRawEmail"]))

    certificate = create_api_certificate(stack, api_domain_name, stack.zone)

    verify_domain_create_call = AwsSdkCall(service="SES",
                                           action="verifyDomainIdentity",
                                           parameters={"Domain": domain},
                                           physical_resource_id_path="VerificationToken")

    verify_domain_identity = AwsCustomResource(
        stack, "VerifyDomainIdentity",
        on_create=verify_domain_create_call,
        policy_statements=[PolicyStatement(resources=["*"], actions=["ses:VerifyDomainIdentity"])])

    aws_route53.TxtRecord(
        stack, "SESVerificationRecord",
        zone=stack.zone,
        record_name=f"_amazonses.{domain}",
        values=[verify_domain_identity.get_data_string("VerificationToken")]
    )

    domain_options = aws_apigateway.DomainNameOptions(domain_name=api_domain_name, certificate=certificate)
    stage_options = aws_apigateway.StageOptions(
        throttling_rate_limit=10,
        throttling_burst_limit=100
    )

    base_api = aws_apigateway.RestApi(
        stack, 'ContactFormAPIGW',
        rest_api_name='ContactFormAPI',
        domain_name=domain_options,
        deploy_options=stage_options
    )

    kix.info("Routing A-Record Alias")
    a_record_target = aws_route53.RecordTarget.from_alias(aws_route53_targets.ApiGateway(base_api))
    aws_route53.ARecord(
        stack, "ApiAliasRecord",
        zone=stack.zone,
        target=a_record_target,
        record_name=api_domain_name)

    api_entity = base_api.root.add_resource(api_path)
    example_entity_lambda_integration = aws_apigateway.LambdaIntegration(
        base_lambda, proxy=False, integration_responses=[get_integration_response()])

    api_entity.add_method(
        'POST', example_entity_lambda_integration,
        method_responses=[get_method_response()])

    add_cors_options(api_entity)


def create_api_certificate(stack: core.Stack, domain: str, zone: aws_route53.HostedZone):
    kix.info("Creating Certificate")
    cert = aws_certificatemanager.DnsValidatedCertificate(
        stack, f"ApiCertificate",
        domain_name=domain,
        hosted_zone=zone)
    core.CfnOutput(stack, 'ApiCertificateArn', value=cert.certificate_arn)
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
