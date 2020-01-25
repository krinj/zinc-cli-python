from aws_cdk import core, aws_route53, aws_s3, aws_certificatemanager, aws_cloudfront, aws_route53_targets, \
    aws_s3_deployment
import os


class CDKStaticSiteStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, project_id: str, domain_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        module_path = os.path.dirname(__file__)

        zone = aws_route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=domain_name,
            private_zone=False)

        # Construct code goes here
        core.CfnOutput(self, "Site", value=f"https://{domain_name}")

        # Content bucket
        site_bucket = aws_s3.Bucket(
            self, "SiteBucket",
            bucket_name=f"static-site.{project_id.lower().replace('_', '-')}",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY)
        core.CfnOutput(self, "BucketArn", value=site_bucket.bucket_arn)

        # Certificate
        cert = aws_certificatemanager.DnsValidatedCertificate(
            self, f"{id}-bucket",
            domain_name=domain_name,
            hosted_zone=zone)
        core.CfnOutput(self, 'CertificateArn', value=cert.certificate_arn)

        distribution = aws_cloudfront.CloudFrontWebDistribution(
            self, "SiteDistribution",
            alias_configuration=aws_cloudfront.AliasConfiguration(
                acm_cert_ref=cert.certificate_arn,
                names=[domain_name],
                ssl_method=aws_cloudfront.SSLMethod.SNI,
                security_policy=aws_cloudfront.SecurityPolicyProtocol.TLS_V1_1_2016,
            ),
            origin_configs=[
                aws_cloudfront.SourceConfiguration(
                    s3_origin_source=aws_cloudfront.S3OriginConfig(s3_bucket_source=site_bucket),
                    behaviors=[aws_cloudfront.Behavior(is_default_behavior=True)]
                )])
        core.CfnOutput(self, "DistributionId", value=distribution.distribution_id)

        # Route 53 alias record for the cloudfront distribution
        aws_route53.ARecord(
            self, "SiteAliasRecord",
            zone=zone,
            target=aws_route53.AddressRecordTarget.from_alias(aws_route53_targets.CloudFrontTarget(distribution)),
            record_name=domain_name)

        aws_s3_deployment.BucketDeployment(
            self, "DeployWithInvalidation",
            sources=[aws_s3_deployment.Source.asset(os.path.join(module_path, "default_source/"))],
            destination_bucket=site_bucket,
            distribution=distribution,
            distribution_paths=["/*"])