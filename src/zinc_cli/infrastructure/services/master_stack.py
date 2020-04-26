import os
from typing import Optional, Dict, List

import kix
from aws_cdk import core, aws_dynamodb, aws_route53, aws_certificatemanager, aws_apigateway, aws_route53_targets, \
    aws_lambda, aws_cognito
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

        # Create the user pool.
        self.user_pool: aws_cognito.UserPool = self._create_user_pool()

        # Create the API Gateway.
        self._rest_api: Optional[aws_apigateway.RestApi] = None
        self._api_authorizer = None
        self._api_map: Dict[str, aws_apigateway.Resource] = {}

    def _create_user_pool(self) -> aws_cognito.UserPool:
        user_pool = aws_cognito.UserPool(
            scope=self,
            id="UserPool",
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True)
        )

        aws_cognito.UserPoolClient(
            scope=self,
            user_pool=user_pool,
            id="AuthClientWeb",
            generate_secret=False
        )

        return user_pool

    def get_rest_api(self):
        if self._rest_api is None:
            self._rest_api = self.create_root_api_gateway(f"apix.{self.domain}")
        return self._rest_api

    def _get_api_entity(self, api_path: str):
        if api_path not in self._api_map:
            self._api_map[api_path] = self.get_rest_api().root.add_resource(api_path)
        api_entity: aws_apigateway.Resource = self._api_map[api_path]
        return api_entity

    def add_api_method(self, api_path: str, method: str, lambda_handler) -> aws_apigateway.Resource:
        # Either look-up or create the API entity.
        api_entity: aws_apigateway.Resource = self._get_api_entity(api_path)

        # Create the Lambda integration out of the provided Lambda handler.
        lambda_integration = aws_apigateway.LambdaIntegration(
            lambda_handler, proxy=False, integration_responses=[self.get_integration_response()])

        # Create the API Method (adding the integration).
        api_entity.add_method(method, lambda_integration, method_responses=[self.get_method_response()])
        self.add_cors_options(api_entity)
        return api_entity

    def add_crud_api(self, api_path: str, lambda_handler_path: str,
                     get_access_auth: bool = False, edit_access_auth: bool = False):

        # Here we add a new CRUD API at the given path.
        # We will use the data-store we've already created.
        # We will create all methods and add all headers and integration responses.
        # We will create proxy methods too.

        # Authorization will depend on whether or not we use it.

        api_function = aws_lambda.Function(
            scope=self,
            id=f"{api_path}Function",
            handler="lambda_handler.handle_crud_request",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": self.public_table.table_name
            },
            code=aws_lambda.Code.asset(lambda_handler_path),
            timeout=core.Duration.seconds(30)
        )

        self.public_table.grant_full_access(api_function)
        api_entity: aws_apigateway.Resource = self._get_api_entity(api_path)

        # Add methods both for the root and the proxy.
        self._add_generic_api_integration(api_entity, api_function, get_access_auth, edit_access_auth, is_proxy=False)
        self._add_generic_api_integration(api_entity, api_function, get_access_auth, edit_access_auth, is_proxy=True)

        return api_entity

    def _add_generic_api_integration(
            self, api_resource: aws_apigateway.Resource, api_function,
            get_access_auth: bool = False, edit_access_auth: bool = False, is_proxy: bool = False):

        api_lambda_integration = aws_apigateway.LambdaIntegration(
            api_function,
            proxy=False,
            integration_responses=[self.get_integration_response()],
            request_templates={"application/json": self.get_request_template()}
        )

        if is_proxy:
            api_lambda_integration_without_response = aws_apigateway.LambdaIntegration(
                api_function,
                proxy=False,
                request_templates={"application/json": self.get_request_template()}
            )
            api_resource = api_resource.add_proxy(
                default_integration=api_lambda_integration_without_response, any_method=False)

        self.add_cors_options(api_resource)
        get_authorizer = self._api_authorizer if get_access_auth else None
        edit_authorizer = self._api_authorizer if edit_access_auth else None

        self._add_generic_api_method(api_resource, api_lambda_integration, ["GET"], get_authorizer)
        self._add_generic_api_method(api_resource, api_lambda_integration, ["POST"], edit_authorizer)

    def _add_generic_api_method(
            self, api_resource: aws_apigateway.Resource, integration: aws_apigateway.LambdaIntegration,
            methods: List[str], authorizer: Optional[aws_apigateway.CfnAuthorizer]):

        auth_type = None if authorizer is None else aws_apigateway.AuthorizationType.COGNITO
        for method in methods:
            api_method = api_resource.add_method(
                method,
                integration,
                method_responses=[self.get_method_response()],
                authorization_type=auth_type
            )

            if authorizer:
                api_method.node.find_child("Resource").add_property_override('AuthorizerId', authorizer.ref)

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

        # Also create the authorizer for this API.
        self._api_authorizer = self.create_root_api_authorizer(self.user_pool, rest_api)
        return rest_api

    def create_root_api_authorizer(
            self, user_pool: aws_cognito.UserPool, api: aws_apigateway.RestApi) -> aws_apigateway.CfnAuthorizer:
        authorizer = aws_apigateway.CfnAuthorizer(
            scope=self,
            name="MasterStackApiAuth",
            id="MasterStackApiAuth",
            type="COGNITO_USER_POOLS",
            provider_arns=[user_pool.user_pool_arn],
            rest_api_id=api.rest_api_id,
            identity_source="method.request.header.Authorization"
        )
        return authorizer

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

    @staticmethod
    def get_request_template() -> str:
        return "{\"auth_sub\": \"$context.authorizer.claims.sub\",\n" \
               "\"method\": \"$context.httpMethod\",\n" \
               "\"body\" : $input.json('$'),\n" \
               "\"queryParams\": {\n" \
               "#foreach($param in $input.params().querystring.keySet())\n" \
               "\"$param\": \"$util.escapeJavaScript($input.params().querystring.get($param))\" #if($foreach.hasNext),#end\n" \
               "#end\n" \
               "},\n" \
               "\"pathParams\": {\n" \
               "#foreach($param in $input.params().path.keySet())\n" \
               "\"$param\": \"$util.escapeJavaScript($input.params().path.get($param))\" #if($foreach.hasNext),#end\n" \
               "#end\n" \
               "}\n" \
               "}\n"
