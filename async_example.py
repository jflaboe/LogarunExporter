from logarun import *
import time

api = API(username="jflaboe")
resp = api.get_date_range("05/19/2015", "12/19/2015", wait_for_completion=False)

while resp.is_complete() is False:
    print(resp.get_remaining_pct())
    time.sleep(10)