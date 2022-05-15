import requests
from bs4 import BeautifulSoup
from datetime import timedelta, date, datetime
import threading

def daterange(start_date, end_date):
    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    end_date = datetime.strptime(end_date, "%m/%d/%Y")
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

BASE_URL = "http://www.logarun.com/"
ONE_DAY = 60 * 60 * 24 #seconds

class LogarunDay:
    def __init__(self, html):
        self.informatics = {}
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find(id = "ctl00_Content_c_dayTitle_c_title").text
        
        #handle title
        if not title == "No Title":
            self.informatics['title'] = title

        note = soup.find(id="ctl00_Content_c_note_c_note").text
        
        if not note == "No Note":
            self.informatics['note'] = note
        else:
            self.informatics['note'] = None
        
        #handle activities
        activites = soup.find(class_='applications').find_all(class_='app')
        data = []
        for activity in activites:
            try:
                info = {}
                info['type'] = activity.find(class_="title").text
                for field in activity.find_all(class_='field'):
                    
                    label = field.findChild("label")
                    stat = field.findChild("span")
                    if not label is None:
                        label = label.text
                    else:
                        label = "Unit"
                    stat = stat.text
                    info[label] = stat
                    if 'title' in self.informatics:
                        info['title'] = title

                    info['note'] = self.informatics['note']
                data.append(info)
            except:
                pass

        if len(activites) > 0:
            self.informatics['activities'] = data
            
        

    def __str__(self):
        return str(self.informatics)
    
    def __repr__(self):
        return self.__str__()

    def get_activities(self):
        if 'activities' in self.informatics:
            return self.informatics['activities']
        
        return []
        

class API:
    def __init__(self, username=None, password=None, workers = 10):
        self.session = requests.Session()
        self.username = username
        self.lock = threading.Lock()
        self.max_workers = workers
        if not password is None and not username is None:
            self._login(username, password)
        

    def _login(self, username, password):
        data = {
            'LoginName': username,
            'Password': password,
            'SubmitLogon': 'true',
            'LoginNow': 'Login'
        }

        response = self.session.post(BASE_URL + 'logon.aspx', data=data)
        response.raise_for_status()

    def get_day(self, date): #date is a datestring (mm/dd/yyyy)
        month, day, year = date.split('/')
        url = BASE_URL + "calendars/" + self.username + "/" + year + "/" + month + "/" + day
        
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        return LogarunDay(resp.content)
    
    def user_exists(self):
        resp = self.session.get(BASE_URL + "xml.aspx?username={}&type=General".format(self.username))
        try:
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content)
        except:
            return False
        has_activities = True
        try:
            activities = soup.find(attrs={"name": "Activities"}).find_all("item")
            if len(activities) < 1:
                has_activities = False
        except:
                has_activities = False

        has_runs = True
        try:
            names = soup.find_all("name")
            for n in names:
                if "Days Run" in n:
                    if n.find_next_sibling().text == "0":
                        has_runs = False
        except:
            has_runs = False
        
        if has_activities or has_runs:
            return True

        return False


    def get_date_range(self, date1, date2, on_add=lambda *args: None, on_complete=lambda *args: None, wait_for_completion=True):
        
        def add_day(s, d, r):
            jobs = []
            while len(d) > 0:
                #get a job
                s.lock.acquire()
                if len(d) > 0:
                    dt = d.pop(0)
                else:
                    s.lock.release()
                    break
                s.lock.release()

                #query Logarun
                r.add_started()
                try:
                    i = s.get_day(dt)
                except:
                    r.add_ended()
                    s.lock.acquire()
                    d.append(dt)
                    s.lock.release()
                    continue
                
                jobs.append(dt)

                #update results
                r.add_value( (dt, i) )
            jobs.sort()

        threads = []
        dates = [dt.strftime("%m/%d/%Y") for dt in daterange(date1, date2)]
        response = APIDateRangeResponse(len(dates), on_add, on_complete)

        for i in range(self.max_workers):
            t = threading.Thread(target=add_day, args=(self, dates, response), name=str(i))
            t.daemon = True
            t.start()
            threads.append(t)

        if wait_for_completion is True:
            for t in threads:
                t.join()
        return response

class APIDateRangeResponse():
    def __init__(self, num_dates, on_add, on_complete):
        self.num_dates = num_dates
        self.unread = []
        self.response = []
        self.finished = False
        self.on_add = on_add
        self.on_complete = on_complete
        self.started = 0
        self.ended = 0
        self.lock = threading.Lock()

    def get_remaining(self):
        return self.num_dates - len(self.response)
    
    def get_remaining_pct(self):
        return (self.num_dates - len(self.response)) / float(self.num_dates) * 100

    def is_complete(self):
        return self.finished

    def mark_complete(self):
        self.finished = True
        self.on_complete()

    def add_value(self, value):
        self.lock.acquire()
        self.unread.append(value)
        self.response.append(value)
        if self.get_remaining() == 0:
            self.mark_complete()
        self.lock.release()

        self.on_add(value)

    def add_started(self):
        self.lock.acquire()
        self.started += 1
        self.lock.release()

    def add_ended(self):
        self.lock.acquire()
        self.ended += 1
        self.lock.release()
    
    def has_available(self):
        if len(self.unread) > 0:
            return True

    def get_available(self):
        self.lock.acquire()
        out = self.unread.copy()
        self.unread = []
        self.lock.release()
        return out

    def get_response(self):
        return self.response



    
    



