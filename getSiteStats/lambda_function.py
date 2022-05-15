import json
import boto3
import os

dynamo = boto3.client("dynamodb")

def lambda_handler(event, context):
    site_data = get_site_data()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "success": True,
            "data": user_data
        }),
        "headers": {
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*"
        }
    }

def dynamo_to_dict(dynamo_response):
    print("dynamo")
    print(dynamo_response)
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
            elif 'L' in v:
                l = []
                for item in v['L']:
                    l.append(unmarshal(item['M']))
                result[k] = l

        return result
    
    return unmarshal(dynamo_response['Item'])

def get_user_data(user_id):
    resp = dynamo.get_item(
        TableName=os.environ["USERS_TABLE_NAME"],
        Key={
            'sid': {
                'S': "all"
            }
        }
    )
    print(resp)

    return dynamo_to_dict(resp)