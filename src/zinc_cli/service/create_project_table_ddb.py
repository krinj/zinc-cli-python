import boto3
from logkit import log


def create_project_table_ddb(table_name: str, region: str):
    client = boto3.client('dynamodb', region_name=region)
    table_name: str = table_name
    key_schema = [_primary_key("resource_type"), _sort_key("resource_id")]
    attributes = [_attribute("resource_type", "S"), _attribute("resource_id", "S")]

    try:

        response = client.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attributes,
            ProvisionedThroughput=_throughput(1, 1)
        )
        log.info("Table Creation Response", str(response))

    except Exception as e:
        log.error("Failed to create Table", e)


# ======================================================================================================================
# Helper Functions
# ======================================================================================================================


def _primary_key(k: str):
    return {
        "AttributeName": k,
        "KeyType": "HASH"
    }


def _sort_key(k: str):
    return {
        "AttributeName": k,
        "KeyType": "RANGE"
    }


def _attribute(k: str, attribute_type: str):
    return {
        "AttributeName": k,
        "AttributeType": attribute_type
    }


def _throughput(read: int, write: int):
    return {
        "ReadCapacityUnits": read,
        "WriteCapacityUnits": write
    }
