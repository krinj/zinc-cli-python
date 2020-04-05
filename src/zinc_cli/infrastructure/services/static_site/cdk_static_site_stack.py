import kix
from aws_cdk import core, aws_route53, aws_s3, aws_certificatemanager, aws_cloudfront, aws_route53_targets
from services.master_stack import CDKMasterStack


def add_static_site(stack: CDKMasterStack, domain: str, bucket_name: str, prefix: str = ""):

    # Construct code goes here
    core.CfnOutput(stack, f"{prefix}Site", value=f"https://{domain}")

    # Content bucket
    kix.info("Bucket Name: " + bucket_name)
    site_bucket = aws_s3.Bucket(
        stack, f"{prefix}SiteBucket",
        bucket_name=bucket_name,
        website_index_document="index.html",
        website_error_document="index.html",
        public_read_access=True,
        removal_policy=core.RemovalPolicy.DESTROY)
    core.CfnOutput(stack, f"{prefix}BucketArn", value=site_bucket.bucket_arn)

    # Certificate
    kix.info("Creating Certificate")
    cert = aws_certificatemanager.DnsValidatedCertificate(
        stack, f"{prefix}ValidatedCert",
        domain_name=domain,
        hosted_zone=stack.zone)
    core.CfnOutput(stack, f"{prefix}CertificateArn", value=cert.certificate_arn)

    kix.info("Creating Distribution")
    distribution = aws_cloudfront.CloudFrontWebDistribution(
        stack, f"{prefix}SiteDistribution",
        alias_configuration=aws_cloudfront.AliasConfiguration(
            acm_cert_ref=cert.certificate_arn,
            names=[domain],
            ssl_method=aws_cloudfront.SSLMethod.SNI,
            security_policy=aws_cloudfront.SecurityPolicyProtocol.TLS_V1_1_2016,
        ),
        origin_configs=[
            aws_cloudfront.SourceConfiguration(
                s3_origin_source=aws_cloudfront.S3OriginConfig(s3_bucket_source=site_bucket),
                behaviors=[aws_cloudfront.Behavior(is_default_behavior=True)]
            )],
        error_configurations=[
            aws_cloudfront.CfnDistribution.CustomErrorResponseProperty(
                error_code=403,
                response_code=200,
                response_page_path="/index.html"
            ),
            aws_cloudfront.CfnDistribution.CustomErrorResponseProperty(
                error_code=404,
                response_code=200,
                response_page_path="/index.html"
            )
        ]
    )
    core.CfnOutput(stack, f"{prefix}DistributionId", value=distribution.distribution_id)
    a_record_target = aws_route53.AddressRecordTarget.from_alias(aws_route53_targets.CloudFrontTarget(distribution))

    # Route 53 alias record for the CloudFront distribution
    kix.info("Routing A-Record Alias")
    aws_route53.ARecord(
        stack, f"{prefix}SiteAliasRecord",
        zone=stack.zone,
        target=a_record_target,
        record_name=domain)

