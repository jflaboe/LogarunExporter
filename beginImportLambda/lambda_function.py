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
    try:
        dynamo.update_item(
            TableName=os.environ["USERS_TABLE_NAME"],
            Key={
                'sid': {
                    'S': str(strava_account["athlete"]["id"])
                }
            },
            UpdateExpression='SET #a = :value',
            ConditionExpression='attribute_not_exists(#a)',
            ExpressionAttributeValues={
                ":value": {
                    "M": {}
                },
            },
            ExpressionAttributeNames={
                '#a': 'requests'
            }
        )
    except:
        print("requests already exist")
    if 'access_token' in strava_account:
        update_expression = "SET access_token = :a, refresh_token = :r, expires_at = :e, requests.#rid = :c"
        expression_attribute_values = {
            ":c":{
                "M": {
                    "start": {
                        "S": request_data["startDate"]
                    },
                    "end": {
                        "S": request_data["endDate"]
                    },
                    "days": {
                        "N": str(len(dates))
                    },
                    "completed": {
                        "N": "0"
                    }
                }
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
    else:
        update_expression = "SET requests.#rid = :c"
        expression_attribute_values = {
            ":c":{
                "M": {
                    "start": {
                        "S": request_data["startDate"]
                    },
                    "end": {
                        "S": request_data["endDate"]
                    },
                    "days": {
                        "N": str(len(dates))
                    },
                    "completed": {
                        "N": "0"
                    }
                }
            }
        }
    expression_attribute_names = {
        "#rid": req_id
    }
    dynamo.update_item(
        TableName=os.environ["USERS_TABLE_NAME"],
        Key={
            'sid': {
                'S': str(strava_account["athlete"]["id"])
            }
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names)
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
            "S": str(strava_account["athlete"]["id"])
        }
    }
    print(expression_attribute_values)
    dynamo.update_item(
        TableName=os.environ["REQUESTS_TABLE_NAME"],
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
    title = None
    if request_data["useDefaultTitle"] is True:
        title = request_data["defaultTitle"]
    print("hey there")
    print(request_data)
    for date in dates:

        r = upload_to_sqs({
            "req_id": req_id,
            "date": date,
            "sid": str(strava_account["athlete"]["id"]),
            "user": user,
            "pass": password,
            "title": title,
            "wm": request_data["useWatermark"]
        })
        
    return req_id

def upload_to_sqs(obj):
    sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=json.dumps(obj)
    )

def daterange(start_date, end_date):
    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    end_date = datetime.strptime(end_date, "%m/%d/%Y")
    for n in range(int ((end_date - start_date).days) + 1):
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
            "statusCode": 200,
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
    if not "sid" in request_data or request_data["sid"] is None:
        strava_account = check_for_account(request_data)
        if strava_account is None:
            strava_account = get_strava_account(request_data)
        print("STRAVA ACCOUNT {}".format(strava_account))

        
        if strava_account is None or not 'access_token' in strava_account:
            return {
                "statusCode": 200,
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
    else:
        strava_account = {
            "athlete": {
                "id": request_data["sid"]
            }
        }
    
    request_id = create_request(request_data, strava_account)

    return {
        "statusCode": 200,
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