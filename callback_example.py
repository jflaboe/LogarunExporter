from logarun import *
import time

def print_value(value):
    print(value)

api = API(username="jflaboe")
resp = api.get_date_range("05/19/2015", "12/19/2015", on_add=print_value, wait_for_completion=False)

while resp.is_complete() is False:
    time.sleep(10)