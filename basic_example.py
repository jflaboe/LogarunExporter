from logarun import *

api = API(username="jflaboe")
resp = api.get_date_range("05/19/2015", "07/19/2016", wait_for_completion=True)
print(resp.get_response())