from aws_cdk import core, aws_lambda
import os


class CDKBookingsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, project_id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        module_path = os.path.dirname(__file__)

        base_lambda = aws_lambda.Function(
            self, f"GetFreeSlots",
            handler="lambda_handler.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            code=aws_lambda.Code.asset(f"{module_path}/lambda"),
        )
