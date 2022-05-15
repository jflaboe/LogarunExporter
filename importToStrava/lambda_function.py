from datetime import datetime, timedelta
import json
import time
import os

import boto3
import logarun
import requests

dynamodb = boto3.client("dynamodb")

def lambda_handler(event, context):
    data = get_data_from_event(event)
    logarun_activities = get_logarun_activities(data)
    activities_added = 0
    distance_added = 0
    if len(logarun_activities) > 0:
        strava_access_token = get_strava_access_token(data)
        added_duration = 0
        
        for activity in logarun_activities:
            if not 'title' in activity and "title" in data and not data["title"] is None:
                activity['title'] = data['title']

            if data["wm"] is True:
                activity['note'] = activity["note"] + "\n\nImported from Logarun"
                
            added_duration, distance, added = upload_activity_to_strava(activity, strava_access_token, data["date"], added_duration=added_duration)
            activities_added += added
            distance_added += distance

    mark_as_complete(data, activities_added, distance_added)
    add_aggregate_stats(data, activities_added, distance_added)


def mark_as_complete(data, activities, distance):
    update_expression = "SET #field.#date = :c"
    expression_attribute_values = {
        ":c":{
            "M": {
                "Complete": {
                    "BOOL": True
                },
                "Distance": {
                    "N": str(distance)
                },
                "Activities": {
                    "N": str(activities)
                }
            } 
        }
    }
    expression_attribute_names = {
        "#field": "dates",
        "#date": data["date"]
    }
    print(expression_attribute_values)
    dynamodb.update_item(
        TableName=os.environ["REQUESTS_TABLE_NAME"],
        Key={
            'rid': {
                'S': data["req_id"]
            }
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names)


    update_expression = "ADD distance :d, activities :a, #req.#rid.#complete :c"
    expression_attribute_values = {
        ":a":{
            "N": str(activities)
        },
        ":d":{
            "N": str(distance)
        },
        ":c":{
            "N": "1"
        }
    }
    expression_attribute_names = {
        "#req": "requests",
        "#rid": data['req_id'],
        "#complete": "completed"
    }
    print(expression_attribute_values)
    dynamodb.update_item(
        TableName=os.environ["USERS_TABLE_NAME"],
        Key={
            'sid': {
                'S': data["sid"]
            }
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names)


def add_aggregate_stats(data, activities, distance):
    update_expression = "ADD distance :d, activities :a"
    expression_attribute_values = {
        ":a":{
            "N": str(activities)
        },
        ":d":{
            "N": str(distance)
        }
    }
    print(expression_attribute_values)
    dynamodb.update_item(
        TableName=os.environ["USERS_TABLE_NAME"],
        Key={
            'sid': {
                'S': "all"
            }
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values)

def get_data_from_event(event):
    return json.loads(event['Records'][0]['body'])

def get_logarun_activities(data):
    lapi = logarun.API(username=data["user"], password=data["pass"])
    return lapi.get_day(data["date"]).get_activities()

def get_strava_access_token(data):
    resp = dynamodb.get_item(
        #TableName=os.environ["USERS_TABLE_NAME"],
        TableName="Users_LogarunToStrava",
        Key={
            'sid': {
                'S': data['sid']
            }
        }
    )

    access_token = resp['Item']['access_token']['S']
    refresh_token =  resp['Item']['refresh_token']['S']
    token_expires_at = int(resp['Item']['expires_at']['N'])
    
    if time.time() > token_expires_at or True:
        #refresh_response = client.refresh_access_token(client_id=os.environ["STRAVA_CLIENT_ID"], client_secret=os.environ['STRAVA_CLIENT_SECRET'], refresh_token=client.refresh_token)
        payload = {
            'client_id': 29352,
            'client_secret': "43186a07784add288935e40d49eddb2701f2f193",
            'refresh_token': refresh_token,
            'grant_type': "refresh_token",
            'f': 'json'
        }
        resp = requests.post("https://www.strava.com/oauth/token", data=payload, verify=False)
        refresh_response = json.loads(resp.content)
    else:
        print(refresh_response)
        update_expression = "SET access_token = :a, refresh_token = :r, expires_at = :e"
        expression_attribute_values = {
            ":a": {
                "S": refresh_response['access_token']
            },
            ":r": {
                "S": refresh_response['refresh_token']
            },
            ":e": {
                "N": str(refresh_response["expires_at"])
            }
        }
        dynamodb.update_item(
            #TableName=os.environ["USERS_TABLE_NAME"],
            TableName="Users_LogarunToStrava",
            Key={
                'sid': {
                    'S': str(data['sid'])
                }
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values)
    
        access_token = refresh_response['access_token']
        refresh_token = refresh_response['refresh_token']
        token_expires_at = refresh_response['expires_at']
    return access_token
def upload_activity_to_strava(activity, strava_access_token, date, added_duration=0):
    
    default_titles = {"run": "Run", "bike": "Bike", "swim": "Swim"}
    atype_map = {"run": "run", "bike": "ride", "swim": "swim"}
    try:
        if not activity['type'].lower().replace("\n", "") in default_titles:
            print("here")
            return
        atype = activity['type'].lower().replace("\n", "")

    except:
        return (0, 0, 0)
        atype = "run"


    if not 'title' in activity:
        activity['title'] = default_titles[atype]

    atype = atype_map[atype]

    try:
        distance = float(activity['Distance'])
        
        unit = activity['Unit']
        

        if 'Mile' in unit:
            distance = distance * 5280 * 12 * 2.54 / 100
        elif 'Yard' in unit:
            distance = distance * 3 * 12 * 2.54 / 100
        elif 'Kilometer' in unit:
            distance = distance / 1000
        

    except:
        distance = 0
    distance = int(distance)
    try:
        hours, minutes, seconds = activity['Time'].split(":")
        duration = 60*60*int(hours) + 60*int(minutes) + int(seconds)
    except:
        speed_map = {"run": 0.298258, "ride": 0.186411, "swim": 1.2}
        if distance > 0:
            duration = int(speed_map[atype] * distance)
        else:
            duration = 0

    iso8601 = datetime.strptime(date, "%m/%d/%Y") + timedelta(seconds=added_duration)
    iso8601 = iso8601.isoformat()
    body = {
        "name": activity['title'],
        "type": atype,
        "start_date_local": iso8601,
        "elapsed_time": duration,
        "distance": distance,
        "trainer": 0,
        "commute": 0,
        "hide_from_home": False

    }
    if not activity['note'] is None:
        body['description'] = activity['note']
    else:
        body['description'] = ""

    headers = {"Authorization": "Bearer {}".format(strava_access_token)}
    print(body)
    resp = requests.post("https://www.strava.com/api/v3/activities", data=body, headers=headers)
    print(resp.content)
    return (duration + added_duration + 3600, distance, 1)