import boto3
import json
import os

sns = boto3.client('sns')

def get_data(event):
    return json.loads(event['body'])

def build_message(data):
    return "User Email:\t{}\n\nMessage:\t{}".format(data['email'], data['help'])

def lambda_handler(event, context):
    sns.publish(
        TopicArn=os.environ["HELP_TOPIC_ARN"],
        Message=build_message(get_data(event)),
        Subject="Help on LogarunToStrava"
    )

    return {
        "code": 200,
        "body": json.dumps({
            "success": True
        }),
        "headers": {
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*"
        }
    }
