import json
import boto3
from botocore.exceptions import ClientError
import os


TARGET_EMAIL_KEY = "TARGET_EMAIL"


def handler(event, context):

    notes = event["notes"] if "notes" in event else "No Notes"
    phone = event["phone"] if "phone" in event else "No Phone"
    name = event["name"] if "name" in event else "No Name"
    email = event["email"] if "email" in event else "hello@zinccli.com"
    email = "hello@zinccli.com" if (len(email) == 0 or "@" not in email) else email

    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "Zinc Admin <hello@zinccli.com>"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    if TARGET_EMAIL_KEY not in os.environ:
        return {"statusCode": "500", "body": "No target email detected."}

    RECIPIENT = os.environ[TARGET_EMAIL_KEY]

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = f"{name} @ Amazon SES Test (SDK for Python)"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                 "This email was sent with Amazon SES using the "
                 "AWS SDK for Python (Boto)." + notes
                 )

    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body>
      <h1>Amazon SES Test (SDK for Python)</h1>
      <p>{name}</p>
      <p>{phone}</p>
      <p>{email}</p>
      <p>{notes}</p>
      <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
          AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>
                """

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    response = {
        'statusCode': 200,
        "body": "No event body was found.",
        "event": event
    }

    # Try to send the email.
    try:
        # Provide the contents of the email.
        ses_response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            ReplyToAddresses=[
                email,
            ],
            Source=SENDER
        )

    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
        response["ses_response"] = e.response['Error']['Message']
    else:
        print("Email sent! Message ID:"),
        print(ses_response['MessageId'])
        response["ses_response"] = "Successful mail sent!"

    return response
