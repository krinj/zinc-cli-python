import uuid
import boto3
import os


DDB_TABLE_NAME = os.environ["TABLE_NAME"]
client = boto3.client('dynamodb')


def any_handler(event, context):
    return {
        "statusCode": 200,
        "body": "YA GOT ME",
        "event": event,
        "context": str(context)
    }


def post_handler(event, context):
    try:
        payload = event["payload"] if "payload" in event else "No Payload"
        result = client.put_item(TableName=DDB_TABLE_NAME, Item={
            "payload": {"S": payload},
            "item_number": {"N": "1"},
            "id": {"S": uuid.uuid4().hex},
        })

        result_payload = str(result)
    except Exception as e:
        result_payload = str(e)

    return {
        'statusCode': 200,
        'body': 'POST CRUD Lambda Invoked Successfully.',
        "payload": result_payload
    }


def get_handler(event, context):

    try:
        result = client.scan(TableName=DDB_TABLE_NAME)
        result_payload = str(result)
    except Exception as e:
        result_payload = str(e)

    print("Event Object", str(event))
    print("Context Object", str(context))

    try:
        sub = context.sub
        email = context.email
        print(sub, email)
    except Exception as e:
        print(e)

    identity = context.identity
    cognito_identity_id = identity.cognito_identity_id
    cognito_identity_pool_id = identity.cognito_identity_pool_id

    print("Content Identity", identity)
    print("Content Identity ID", cognito_identity_id)
    print("Content Identity Pool ID", cognito_identity_pool_id)

    return {
        'statusCode': 200,
        'body': 'GET CRUD Lambda Invoked Successfully.',
        "payload": result_payload,
        "cognito_id": cognito_identity_id,
        "event": str(event),
        "content": str(context)
    }
