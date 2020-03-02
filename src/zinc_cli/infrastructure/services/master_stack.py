import os

import kix
from aws_cdk import core
from aws_cdk.aws_route53 import HostedZone


class CDKMasterStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, domain: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.stack_module_path: str = os.path.dirname(__file__)

        self.zone: HostedZone = HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=domain,
            private_zone=False)

        kix.info(f"Zone from look-up: {self.zone.zone_name}")
