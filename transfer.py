from stravalib.client import Client
from flask import Flask, redirect, request, render_template
from logarun import API
from datetime import datetime, timedelta
from app_data import *
from wtforms import Form, BooleanField, StringField, PasswordField, DateField, validators
import random
import time
from threading import Thread
ONE_HOUR = 3600

def remove_stale_orders(jobs):
    now = time.time()
    stale = []
    for transaction, job in jobs.items():
        
        if now - job["last_action"] > ONE_HOUR:
            stale.append(transaction)
        try:
            dt = job["date"]
            ed = job["end"]
            if datetime.strptime(dt, "%m/%d/%Y") > datetime.strptime(ed, "%m/%d/%Y"):
                stale.append(transaction)
        except:
            pass
    
    for transaction in stale:
        jobs.pop(transaction, None)
        

def get_next_day(dt):
    dt = datetime.strptime(dt, "%m/%d/%Y")
    dt = dt + timedelta(days=1)
    return dt.strftime("%m/%d/%Y")


def make_step(job):
    time.sleep(1.5)
    if not "end" in job:
        return
    dt = job["date"]
    
    ed = job["end"]
   
    print(dt)
    iso8601 = datetime.strptime(dt, "%m/%d/%Y").strftime("%Y-%m-%d")
    job["date"] = get_next_day(dt)
    job["last_action"] = time.time()
    strava = job["client"]
    logarun = job["logarun_client"]
    data = logarun.get_day(dt).informatics
    try:
        title = data['title']
    except:
        title = "Imported from Logarun"

    try:
        note = data['note']
    except:
        note = "n/a"
    num_uploaded = 0
    if not 'activities' in data:
        return
    
    for activity in data['activities']:
        post = True
        try:
            if not 'run' in activity['type'].lower():
                post = False
            atype = activity['type'].lower().replace("\n", "")

        except:
            atype = "run"

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
            duration = 0
        if post is True:
            strava.create_activity(title, atype, iso8601, duration, description=note, distance=distance)
            
            



        


    


class TransferForm(Form):
    username = StringField('username')
    password = PasswordField('password', [
        validators.DataRequired()
    ])
    start_date = DateField('start_date', format="%m/%d/%Y")
    end_date = DateField('end_date', format="%m/%d/%Y")
    state = StringField('state')

jobs = {}
def process_loop():
    while True:
        remove_stale_orders(jobs)
        for transaction_id, job in jobs.items():
            make_step(job)
        time.sleep(0.5)
        

loop = Thread(target=process_loop)
loop.start()




app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to Logarun to Strava Transfer\n\
    Click <a href=/authorize>here</a> to start"


@app.route("/authorize", methods=['GET'])
def authorize():
    transaction_id = str(int(random.uniform(0, 1) * 10000000))
    jobs[transaction_id] = {}
    jobs[transaction_id]["last_action"] = time.time()
    jobs[transaction_id]["client"] = Client()
    client = jobs[transaction_id]["client"]
    return redirect(client.authorization_url(client_id=CLIENT_ID, redirect_uri="http://127.0.0.1:5000/start_transfer", scope="write", state=transaction_id))


@app.route("/start_transfer", methods=['GET'])
def start_transfer():
    

    
    if request.method == 'GET':
        transaction_id = request.args.get('state')
        client = jobs[transaction_id]["client"]
        jobs[transaction_id]["last_action"] = time.time()
        access_token = client.exchange_code_for_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=request.args.get('code'))
        client.access_token = access_token
        jobs[transaction_id]["access_token"] = access_token
        return render_template("logarun_form.html", state=transaction_id)

    else:
        return "Failed"

    
@app.route("/begin_transfer", methods=['GET'])
def begin_transfer():

    transaction_id = request.args.get('state')
    username = request.args.get('username')
    password = request.args.get('password')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    jobs[transaction_id]["last_action"] = time.time()
    jobs[transaction_id]["logarun_client"] = API(username, password)
    jobs[transaction_id]["date"] = start_date
    jobs[transaction_id]["end"] = end_date
    print(jobs)
    return "Done"

        
        