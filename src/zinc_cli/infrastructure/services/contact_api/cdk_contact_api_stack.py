import kix
from aws_cdk import (
    core,
    aws_lambda,
    aws_apigateway,
    aws_certificatemanager, aws_route53, aws_route53_targets, aws_iam)
import os

from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.custom_resources import AwsCustomResource, AwsSdkCall, PhysicalResourceId, AwsCustomResourcePolicy
from services.master_stack import CDKMasterStack


def add_contact_api(stack: CDKMasterStack, project_name: str, domain: str, forwarding_email: str):

    module_path = os.path.dirname(__file__)
    lambda_path = os.path.join(module_path, "lambda")
    api_path = "contact"

    base_lambda = aws_lambda.Function(
        stack, 'ContactFormLambda',
        handler='lambda_handler.handler',
        runtime=aws_lambda.Runtime.PYTHON_3_7,
        environment={
            "TARGET_EMAIL": forwarding_email,
            "SENDER_EMAIL": f"contact@{domain}",
            "SENDER_NAME": f"{project_name.capitalize()}",
            "SENDER": f"{project_name.capitalize()} Contact Form <contact@{domain}>"
        },
        code=aws_lambda.Code.asset(lambda_path),
    )

    base_lambda.add_to_role_policy(aws_iam.PolicyStatement(
        effect=aws_iam.Effect.ALLOW,
        resources=["*"],
        actions=["ses:SendEmail", "ses:SendRawEmail"]))

    verify_domain_create_call = AwsSdkCall(service="SES",
                                           action="verifyDomainIdentity",
                                           parameters={"Domain": domain},
                                           physical_resource_id=PhysicalResourceId.from_response("VerificationToken"))

    policy_statement = PolicyStatement(actions=["ses:VerifyDomainIdentity"], resources=["*"])
    verify_domain_identity = AwsCustomResource(
        stack, "VerifyDomainIdentity",
        on_create=verify_domain_create_call,
        policy=AwsCustomResourcePolicy.from_statements(statements=[policy_statement])
    )

    aws_route53.TxtRecord(
        stack, "SESVerificationRecord",
        zone=stack.zone,
        record_name=f"_amazonses.{domain}",
        values=[verify_domain_identity.get_response_field("VerificationToken")]
    )

    stack.add_api_method(api_path, "POST", base_lambda)


