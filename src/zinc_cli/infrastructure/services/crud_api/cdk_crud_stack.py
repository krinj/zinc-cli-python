import kix
from aws_cdk import (
    core,
    aws_lambda,
    aws_apigateway,
    aws_certificatemanager, aws_route53, aws_route53_targets)
import os


class CDKCrudApiStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain: str, **kwargs, ) -> None:
        super().__init__(scope, id, **kwargs)
        module_path = os.path.dirname(__file__)
        lambda_path = os.path.join(module_path, "lambda")
        api_domain_name = f"api.{domain}"

        base_lambda = aws_lambda.Function(
            self, 'ApiCorsLambda',
            handler='lambda_handler.handler',
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset(lambda_path),
        )

        zone = aws_route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=domain,
            private_zone=False)
        kix.info(f"Zone from look-up: {zone.zone_name}")

        certificate = self.create_certificate(api_domain_name, zone)

        api_domain_name = f"api.{domain}"
        domain_options = aws_apigateway.DomainNameOptions(domain_name=api_domain_name, certificate=certificate)
        stage_options = aws_apigateway.StageOptions(
            throttling_rate_limit=10,
            throttling_burst_limit=100
        )
        base_api = aws_apigateway.RestApi(
            self, 'ApiGatewayWithCors',
            rest_api_name='ApiGatewayWithCors',
            domain_name=domain_options,
            deploy_options=stage_options
        )

        kix.info("Routing A-Record Alias")
        a_record_target = aws_route53.RecordTarget.from_alias(aws_route53_targets.ApiGateway(base_api))
        aws_route53.ARecord(
            self, "ApiAliasRecord",
            zone=zone,
            target=a_record_target,
            record_name=api_domain_name)

        example_entity = base_api.root.add_resource('example')
        example_entity_lambda_integration = aws_apigateway.LambdaIntegration(
            base_lambda, proxy=False, integration_responses=[self.get_integration_response()])

        example_entity.add_method(
            'GET', example_entity_lambda_integration,
            method_responses=[self.get_method_response()])

        self.add_cors_options(example_entity)

    def create_certificate(self, domain: str, zone: aws_route53.HostedZone):
        kix.info("Creating Certificate")
        cert = aws_certificatemanager.DnsValidatedCertificate(
            self, f"ApiCertificate",
            domain_name=domain,
            hosted_zone=zone)
        core.CfnOutput(self, 'CertificateArn', value=cert.certificate_arn)
        return cert

    @staticmethod
    def add_cors_options(api_gateway_resource):
        api_gateway_resource.add_method(
            'OPTIONS',
            aws_apigateway.MockIntegration(
                integration_responses=[CDKCrudApiStack.get_options_integration_response()],
                passthrough_behavior=aws_apigateway.PassthroughBehavior.WHEN_NO_MATCH,
                request_templates={"application/json": "{\"statusCode\":200}"}),
            method_responses=[CDKCrudApiStack.get_options_method_response()])

    @staticmethod
    def get_integration_response():
        integration_response = aws_apigateway.IntegrationResponse(
            status_code="200",
            response_parameters={'method.response.header.Access-Control-Allow-Origin': "'*'"})
        return integration_response

    @staticmethod
    def get_method_response():
        method_response = aws_apigateway.MethodResponse(
            status_code="200",
            response_parameters={'method.response.header.Access-Control-Allow-Origin': True})
        return method_response

    @staticmethod
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

    @staticmethod
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
