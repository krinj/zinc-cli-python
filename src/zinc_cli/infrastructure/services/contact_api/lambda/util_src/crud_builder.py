import os
from .crud_service import CrudService
from .crud_api import CrudApi


class CrudBuilder:

    def __init__(self, pk: str):
        table_name = os.environ["TABLE_NAME"]
        self.service = CrudService(table_name, pk)
        self.api = CrudApi(self.service)

    def get_api(self):
        return self.api
