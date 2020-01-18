import os
import uuid

import boto3
import yaml
from logkit import log

from zinc_cli.models.base_model import BaseModel
from zinc_cli.service.create_project_table_ddb import create_project_table_ddb


class ProjectDefinitionModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.project_name: str = "MyProject"
        self.project_id: str = uuid.uuid4().hex
        self.resource_id: str = uuid.uuid4().hex
        self.resource_type: str = "PROJECT_DEFINITION"
        self.model_path: str = ""

        # Cloud resources.
        self._table_region = "ap-southeast-2"

    def _get_table_name(self):
        return f"zinc.project.{self.project_name}"

    def serialize(self):
        # Get serialized to a JSON Object.
        payload = {
            "project_name": self.project_name,
            "project_id": self.project_id,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type
        }
        return payload

    def get_local_path(self):
        return os.path.join(self.model_path, "project_definition.yaml")
        pass

    def save_to_local(self):
        # Saves the definition file locally.
        payload = self.serialize()
        path = self.get_local_path()
        with open(path, "w") as file:
            yaml.dump(payload, file)

    def save_to_cloud(self):
        dynamodb = boto3.resource('dynamodb', region_name=self._table_region)
        table = dynamodb.Table(self._get_table_name())
        log.info("DB Table", table)

        item = self.serialize()
        log.info("PutItem", item)

        try:
            response = table.put_item(Item=item)
            log.info("Success", response)
        except Exception as e:
            log.error("Error", e)
        pass

    def create_table(self):
        create_project_table_ddb(self._get_table_name(), self._table_region)
