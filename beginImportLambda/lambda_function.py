import boto3
import json
import logarun
from . import strava
import random
import string
from datetime import timedelta, datetime
import os

sqs = boto3.client('sqs')
dynamo = boto3.client('dynamodb')
queue_url = os.environ['SQS_QUEUE_URL']


def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def create_request(request_data, strava_account):
    dates = [dt.strftime("%m/%d/%Y") for dt in daterange(request_data["startDate"], request_data["endDate"])]
    req_id = id_generator()
    #create user level data
    update_expression = "SET access_token = :a, refresh_token = :r, expires_at = :e, requests = list_append(if_not_exists(requests, :empty_list), :c)"
    expression_attribute_values = {
        ":c":{
            "L": [{
                "M": {
                    "rid": {
                        "S": req_id
                    },
                    "start": {
                        "S": request_data["startDate"]
                    },
                    "end": {
                        "S": request_data["endDate"]
                    }
                }
            }]
        },
        ":empty_list": {
            "L" :[]
        },
        ":a": {
            "S": strava_account['access_token']
        },
        ":r": {
            "S": strava_account['refresh_token']
        },
        ":e": {
            "N": str(strava_account["expires_at"])
        }
    }
    dynamo.update_item(
        TableName='Users_LogarunToStrava',
        Key={
            'sid': {
                'S': str(strava_account["athlete"]["id"])
            }
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values)
    #create request
    update_expression = "SET dates = :c, sid = :b"
    expression_attribute_values = {
        ":c":{
            "M": {
                d: {
                    "M": {
                        "Complete": {
                            "BOOL": False
                        },
                        "Retries": {
                            "N" : "0"
                        }
                    }
                } for d in dates
            }
        },
        ":b": {
            "S": strava_account["athlete"]["id"]
        }
    }
    print(expression_attribute_values)
    dynamo.update_item(
        TableName='Requests_LogarunToStrava',
        Key={
            'rid': {
                'S': req_id
            }
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values)

    #upload to sqs
    password = None
    if not request_data['password'] == "":
        password = request_data["password"]
    user = request_data['username']
    for date in dates:
        upload_to_sqs({
            "req_id": req_id,
            "date": date,
            "sid": str(strava_account["athlete"]["id"]),
            "user": user,
            "pass": password
        })

def upload_to_sqs(obj):
    sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=json.dumps(obj)
    )

def daterange(start_date, end_date):
    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    end_date = datetime.strptime(end_date, "%m/%d/%Y")
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_request_data(event):
    return json.loads(event['body'])

def get_strava_account(request_data):
    return strava.get_strava_account(request_data['accessToken'])

def verify_logarun_account(request_data):
    password = None
    if not request_data['password'] == "":
        password = request_data["password"]

    api = logarun.API(username=request_data['username'], password=password)
    return api.user_exists()

def check_for_account(request_data):
    if "lastRequest" in request_data:
        return None
    else:
        return None

def lambda_handler(event, context):
    
    request_data = get_request_data(event)

    print("REQUEST: {}".format(request_data))

    if verify_logarun_account(request_data) is False:
        return {
            "code": 200,
            "body": json.dumps({
                "success": False,
                "reason": "logarun-account-verification-failed"
            }),
            "headers": {
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*"
            }
        }
    strava_account = check_for_account(request_data)
    if strava_account is None:
        strava_account = get_strava_account(request_data)
    print("STRAVA ACCOUNT {}".format(strava_account))
    if strava_account is None or not 'access_token' in strava_account:
        return {
            "code": 200,
            "body": json.dumps({
                "success": False,
                "reason": "strava-account-verification-failed"
            }),
            "headers": {
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*"
            }
        }
    
    request_id = create_request(request_data, strava_account)

    return {
        "code": 200,
        "body": json.dumps({
            "success": True,
            "requestId": request_id,
            "sid": strava_account["athlete"]["id"]
        }),
        "headers": {
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*"
        }
    }