import boto3
import json
import os

dynamo = boto3.client('dynamodb')

def get_data(event):
    return json.loads(event['body'])

def dynamo_to_dict(dynamo_response):
    def unmarshal(dynamo_map):
        result = {}
        for k, v in dynamo_map.items():
            if 'M' in v:
                result[k] = unmarshal(v['M'])
            elif 'S' in v:
                result[k] = v['S']
            elif 'N' in v:
                result[k] = int(v['N'])
            elif 'BOOL' in v:
                result[k] = v['BOOL']

        return result
    
    return unmarshal(dynamo_response['Item'])

def get_import_request(data):
    resp = dynamo.get_item(
        TableName=os.environ["REQUESTS_TABLE_NAME"],
        Key={
            'rid': {
                'S': data["requestId"]
            }
        }
    )

    return dynamo_to_dict(resp)

def lambda_handler(event, context):
    d = get_import_request(get_data(event))

    return {
        "code": 200,
        "body": json.dumps({
            "success": True,
            "data": d
        }),
        "headers": {
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*"
        }
    }
