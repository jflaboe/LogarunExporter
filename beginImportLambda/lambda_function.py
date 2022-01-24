import boto3
import json
import logarun
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

    #create request
    

    #upload to sqs
    
    for date in dates:
        upload_to_sqs({
            "req_id": req_id,
            "date": date,
            "sid": strava_account["id"]
        })

def upload_to_sqs(obj):
    sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageAttributes={
            'RequestId': {
                'DataType': 'String',
                'StringValue': obj['req_id']
            },
            'Date': {
                'DataType': 'String',
                'StringValue': obj['date']
            },
            'Sid': {
                'DataType': 'String',
                'StringValue': obj['sid']
            }
        }
    )


def daterange(start_date, end_date):
    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    end_date = datetime.strptime(end_date, "%m/%d/%Y")
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def get_request_data(event):
    pass

def get_strava_account(request_data):
    pass

def verify_logarun_account(request_data):
    password = None
    if not request_data['password'] == "":
        password = request_data["password"]

    api = logarun.API(username=request_data['username'], password=password)
    return api.user_exists()

def lamdba_handler(event, context):
    
    request_data = get_request_data(event)

    if verify_logarun_account(request_data) is False:
        return {
            "code": 400,
            "body": json.dumps({
                "reason": "logarun-account-does-not-exist"
            })
        }
    strava_account = get_strava_account(request_data)
    if strava_account is None:
        return {
            "code": 400,
            "body": json.dumps({
                "reason": "strava-account-does-not-exist"
            })
        }
    
    request_id = create_request(request_data, strava_account)