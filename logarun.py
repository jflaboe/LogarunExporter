import requests
from bs4 import BeautifulSoup
from datetime import timedelta, date, datetime

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
                data.append(info)
            except:
                pass

        if len(activites) > 0:
            self.informatics['activities'] = data
            
        note = soup.find(id="ctl00_Content_c_note_c_note").text
        
        if not note == "No Note":
            self.informatics['note'] = note
        

        


class API:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.username = username
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
        
        resp = self.session.get(url)
        resp.raise_for_status()
        return LogarunDay(resp.content)


    def get_date_range(self, date1, date2):
        for dt in daterange(date1, date2):
            yield self.get_day(dt.strftime("%m/%d/%Y"))


