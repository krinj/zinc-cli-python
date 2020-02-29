import json


def handler(event, context):

    response = {
        'statusCode': 200,
        "body": "No event body was found."
    }

    if "body" in event:
        response["body"] = json.loads(event["body"])

    return response
