import requests
import json
import os

AUTH_URL = "https://www.strava.com/api/v3/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def get_strava_account(strava_access_token):
    payload = {
        'client_id': os.environ['STRAVA_CLIENT_ID'],
        'client_secret': os.environ['STRAVA_CLIENT_SECRET'],
        'code': strava_access_token,
        'grant_type': "authorization_code",
        'f': 'json'
    }
    resp = requests.post(AUTH_URL, data=payload, verify=False)
    return json.loads(resp.content)