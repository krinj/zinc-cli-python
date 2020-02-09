from aws_cdk import (
    core,
    aws_lambda,
    aws_apigateway,
)
import os


class CDKCrudApiStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        module_path = os.path.dirname(__file__)
        lambda_path = os.path.join(module_path, "lambda")

        base_lambda = aws_lambda.Function(
            self, 'ApiCorsLambda',
            handler='lambda_handler.handler',
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset(lambda_path),
        )

        base_api = aws_apigateway.RestApi(
            self, 'ApiGatewayWithCors',
            rest_api_name='ApiGatewayWithCors')

        example_entity = base_api.root.add_resource('example')
        example_entity_lambda_integration = aws_apigateway.LambdaIntegration(
            base_lambda, proxy=False, integration_responses=[self.get_integration_response()])

        example_entity.add_method(
            'GET', example_entity_lambda_integration,
            method_responses=[self.get_method_response()])

        self.add_cors_options(example_entity)

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
