import uuid

import kix
from aws_cdk import core, aws_route53, aws_s3, aws_certificatemanager, aws_cloudfront, aws_route53_targets, \
    aws_s3_deployment
import os


class CDKStaticSiteStack(core.Stack):

    def __init__(self, scope: core.Construct,
                 id: str,
                 project_id: str,
                 root_domain: str,
                 sub_domain: str,
                 **kwargs) -> None:

        super().__init__(scope, id, **kwargs)
        module_path = os.path.dirname(__file__)

        zone = aws_route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=root_domain,
            private_zone=False)
        kix.info(f"Zone from look-up: {zone.zone_name}")

        # Compose the full domain.
        if sub_domain is not None and len(sub_domain) > 0:
            full_domain_name = f"{sub_domain}.{root_domain}"
        else:
            full_domain_name = root_domain

        # Construct code goes here
        core.CfnOutput(self, "Site", value=f"https://{full_domain_name}")

        # Content bucket
        bucket_name: str = f"{project_id.lower().replace('_', '-')}.zinc.static-site"
        print("Bucket Name: " + bucket_name)
        site_bucket = aws_s3.Bucket(
            self, "SiteBucket",
            bucket_name=bucket_name,
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            removal_policy=core.RemovalPolicy.DESTROY)
        core.CfnOutput(self, "BucketArn", value=site_bucket.bucket_arn)

        # Certificate
        kix.info("Creating Certificate")
        cert = aws_certificatemanager.DnsValidatedCertificate(
            self, f"{id}-bucket",
            domain_name=full_domain_name,
            hosted_zone=zone)
        core.CfnOutput(self, 'CertificateArn', value=cert.certificate_arn)

        kix.info("Creating Distribution")
        distribution = aws_cloudfront.CloudFrontWebDistribution(
            self, "SiteDistribution",
            alias_configuration=aws_cloudfront.AliasConfiguration(
                acm_cert_ref=cert.certificate_arn,
                names=[full_domain_name],
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
        kix.info("Routing A-Record Alias")
        aws_route53.ARecord(
            self, "SiteAliasRecord",
            zone=zone,
            target=aws_route53.AddressRecordTarget.from_alias(aws_route53_targets.CloudFrontTarget(distribution)),
            record_name=full_domain_name)

        kix.info("Sample Bucket Deployment")
        aws_s3_deployment.BucketDeployment(
            self, "DeployWithInvalidation",
            sources=[aws_s3_deployment.Source.asset(os.path.join(module_path, "default_source/"))],
            destination_bucket=site_bucket,
            distribution=distribution,
            distribution_paths=["/*"])
