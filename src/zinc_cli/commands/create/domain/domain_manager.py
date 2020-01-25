import subprocess
import boto3
from botocore.client import BaseClient

# ======================================================================================================================
# Singleton Methods.
# ======================================================================================================================


class DomainManager:

    _AWS_CLIENT = None

    @staticmethod
    def _client() -> BaseClient:
        if DomainManager._AWS_CLIENT is None:
            DomainManager._AWS_CLIENT = boto3.client("route53domains", region_name="us-east-1")
        return DomainManager._AWS_CLIENT

    @staticmethod
    def validate(domain_name: str):
        try:
            domain_name = domain_name.lower()
            domain_split = domain_name.split(".")
            domain_sections = len(domain_split)
            if domain_sections < 2 or domain_sections > 3:
                return False

            for domain_str in domain_split:
                if not domain_str.isalnum():
                    return False

            return True
        except Exception as e:
            print("validation failure", e)
        return False

    @staticmethod
    def user_owns_domain(domain_name: str):
        is_domain_owned = False

        try:
            response = DomainManager._client().get_domain_detail(DomainName=domain_name)
            is_domain_owned = True
            print(response)
        except Exception as e:
            print("Unable to find domain: ", str(e))

        print(f"Domain Check Result: {domain_name}, owned: {is_domain_owned}")
        return is_domain_owned

    @staticmethod
    def is_domain_available(domain_name: str):

        is_available = False

        try:
            response = DomainManager._client().check_domain_availability(DomainName=domain_name)
            availability_status = response["Availability"]
            is_available = availability_status == "AVAILABLE"
            print(availability_status)
        except Exception as e:
            print("Unable to find domain: ", str(e))

        return is_available
