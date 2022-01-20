import logarun
import time

api = logarun.API('jflaboe', 'runner97')
result = api.get_day("07/15/2015")




for day in api.get_date_range("07/15/2015", "07/22/2016"):
    if 'title' in day.informatics:
        title = str(day.informatics['title'])
    else:
        title = "No Title"
    
    if 'activities' in day.informatics:
        activities = str(len(day.informatics['activities']))
    else:
        activities = "0"

    print(title + ":\t" + activities)