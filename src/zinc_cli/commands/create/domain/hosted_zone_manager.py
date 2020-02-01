import boto3
import kix


class HostedZoneManager:

    @staticmethod
    def has_hosted_zone(domain: str):
        client = boto3.client('route53')
        zones = client.list_hosted_zones_by_name(DNSName=domain)

        kix.info(f"Got hosted zones: {zones}")
        if not zones:
            return False

        hosted_zones = zones['HostedZones']
        kix.info(f"Got hosted zones: {hosted_zones}")
        if len(hosted_zones) == 0:
            return False

        # Check if zone exists in the response.
        # AWS returns the requested zone as index 0 if it exists.
        if domain in hosted_zones[0]["Name"]:
            return True

        return False
