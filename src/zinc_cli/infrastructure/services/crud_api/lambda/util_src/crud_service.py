import uuid
from typing import Union, Dict

import boto3
from boto3.dynamodb.conditions import Key

from .crud_item import CrudItem


class CrudService:

    # Extend this class to fit the CRUD service type we are building.

    def __init__(self, table_name: str, default_pk: str = "ITEM"):
        self.client = boto3.client('dynamodb')
        self.table_name: str = table_name
        self.default_pk: str = default_pk

        dynamodb_resource = boto3.resource('dynamodb')
        self.table = dynamodb_resource.Table(self.table_name)

    def get_default_pk(self) -> str:
        return self.default_pk

    def get_default_sk(self) -> str:
        return uuid.uuid4().hex

    def put_item(self, item: CrudItem):
        item_payload = item.to_ddb_item()
        return self.client.put_item(TableName=self.table_name, Item=item_payload)

    def put_item_from_request_body(self, body: dict):
        item = CrudItem(self.get_default_pk(), self.get_default_sk(), body)
        return self.put_item(item)

    def put_item_with_keys(self, pk: str, sk: str, fields: Dict[str, Union[str, int, float]] = {}):
        payload: dict = {
            "pk": pk,
            "sk": sk
        }

        for k, v in fields.items():
            payload[k] = v

        return self.client.put_item(TableName=self.table_name, Item=payload)

    def get_item(self, partition_key: str, sort_key: str):
        response = self.table.get_item(
            TableName=self.table_name,
            Key={"pk": partition_key, "sk": sort_key}
        )

        print(response)
        return response

    def get_item_range(self, partition_key: str, limit: int = 10):
        response = self.table.query(
            TableName=self.table_name,
            KeyConditionExpression=Key('pk').eq(partition_key),
            Limit=limit
        )

        print(response)
        return response
