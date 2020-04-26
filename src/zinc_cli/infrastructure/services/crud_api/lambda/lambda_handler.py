import os
from util_src.crud_api import CrudApi
from util_src.crud_service import CrudService

DDB_TABLE_NAME = os.environ["TABLE_NAME"]
service = CrudService(DDB_TABLE_NAME, "CRUD_ITEM")
crud_api = CrudApi(service)


def handle_crud_request(event, context):

    result = crud_api.handle_rest_request(event, context)

    return {
        "statusCode": 200,
        "body": "NEW GENERIC CRUD TEST",
        "event": event,
        "context": str(context),
        "result": result
    }
