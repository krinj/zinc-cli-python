from util_src.crud_builder import CrudBuilder

api = CrudBuilder("MENU_ITEMS").get_api()


def handle_crud_request(event, context):

    result = api.handle_rest_request(event, context)

    return {
        "statusCode": 200,
        "body": "NEW GENERIC CRUD TEST",
        "event": event,
        "context": str(context),
        "result": result
    }
