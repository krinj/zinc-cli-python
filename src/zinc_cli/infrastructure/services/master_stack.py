import os
from typing import Optional, Dict

import kix
from aws_cdk import core, aws_dynamodb, aws_route53, aws_certificatemanager, aws_apigateway, aws_route53_targets
from aws_cdk.aws_route53 import HostedZone


class CDKMasterStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain: str, **kwargs) -> None:

        super().__init__(scope, id, **kwargs)
        self.stack_module_path: str = os.path.dirname(__file__)
        self.construct_id: str = id
        self.domain: str = domain

        # Create the hosted zone.
        self.zone: HostedZone = HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=domain,
            private_zone=False)
        kix.info(f"Zone from look-up: {self.zone.zone_name}")

        # Create the data table.
        self.public_table: aws_dynamodb.Table = self.create_table("public_crud", "PublicCrudTable")

        # Create the API Gateway.
        self._rest_api: Optional[aws_apigateway.RestApi] = None
        self._api_map: Dict[str, aws_apigateway.Resource] = {}

    def get_rest_api(self):
        if self._rest_api is None:
            self._rest_api = self.create_root_api_gateway(f"apix.{self.domain}")
        return self._rest_api

    def add_api_method(self, api_path: str, method: str, lambda_handler) -> aws_apigateway.Resource:
        rest_api = self.get_rest_api()

        # Either look-up or create the API entity.
        if api_path not in self._api_map:
            self._api_map[api_path] = rest_api.root.add_resource(api_path)
        api_entity: aws_apigateway.Resource = self._api_map[api_path]

        # Create the Lambda integration out of the provided Lambda handler.
        lambda_integration = aws_apigateway.LambdaIntegration(
            lambda_handler, proxy=False, integration_responses=[self.get_integration_response()])

        # Create the API Method (adding the integration).
        api_entity.add_method(method, lambda_integration, method_responses=[self.get_method_response()])
        self.add_cors_options(api_entity)
        return api_entity

    def create_root_api_gateway(self, api_domain_name: str):

        """ We need this to create the root API Gateway resource. """
        certificate = self.create_api_certificate(api_domain_name, self.zone)
        domain_options = aws_apigateway.DomainNameOptions(domain_name=api_domain_name, certificate=certificate)
        stage_options = aws_apigateway.StageOptions(
            throttling_rate_limit=10,
            throttling_burst_limit=100
        )

        rest_api = aws_apigateway.RestApi(
            self, 'PublicCrudApi',
            rest_api_name='PublicCrudApi',
            domain_name=domain_options,
            deploy_options=stage_options
        )

        kix.info("Routing A-Record Alias for REST API")
        a_record_target = aws_route53.RecordTarget.from_alias(aws_route53_targets.ApiGateway(rest_api))
        aws_route53.ARecord(
            self, "PublicCrudApiAliasRecord",
            zone=self.zone,
            target=a_record_target,
            record_name=api_domain_name)

        return rest_api

    def create_api_certificate(self, domain: str, zone: aws_route53.HostedZone):
        kix.info("Creating Certificate")
        cert = aws_certificatemanager.DnsValidatedCertificate(
            self, f"ApiCertificate",
            domain_name=domain,
            hosted_zone=zone)
        core.CfnOutput(self, 'ApiCertificateArn', value=cert.certificate_arn)
        return cert

    def create_table(self, table_name: str, construct_id: str) -> aws_dynamodb.Table:

        partition_key_attr = aws_dynamodb.Attribute(name="pk", type=aws_dynamodb.AttributeType.STRING)
        sort_key_attr = aws_dynamodb.Attribute(name="sk", type=aws_dynamodb.AttributeType.STRING)

        table = aws_dynamodb.Table(
            scope=self,
            id=construct_id,
            table_name=table_name,
            partition_key=partition_key_attr,
            sort_key=sort_key_attr,
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=core.RemovalPolicy.DESTROY)

        return table

    @staticmethod
    def add_cors_options(api_gateway_resource: aws_apigateway.Resource):
        api_gateway_resource.add_method(
            'OPTIONS',
            aws_apigateway.MockIntegration(
                integration_responses=[CDKMasterStack.get_options_integration_response()],
                passthrough_behavior=aws_apigateway.PassthroughBehavior.WHEN_NO_MATCH,
                request_templates={"application/json": "{\"statusCode\":200}"}),
            method_responses=[CDKMasterStack.get_options_method_response()])

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
