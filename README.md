# LogarunExporter

## Setup

1) Install python
2) Clone the repository
```
git clone https://github.com/jflaboe/LogarunExporter.git
```
3) Setup the virtualenv
```
# install virtualenv
pip install virtualenv

# create the virtualenv
python -m venv env

# activate the env (Windows)
env\Scripts\activate

# activate the env (Unix)
env/bin/activate

# install dependencies
pip install -r requirements.txt
```

4) run examples

```
python callback_example.py
```

## API

### Import
I haven't put this into a package so just create your own scripts within the repository on the top level for simplicity.

```
#import statement
import logarun
```

### Instantiating the API:
```
# without password
api = logarun.API(username="jflaboe")

# with password: necessary if your account is not private
api = logarun.API(username="jflaboe", password="s3cr3tp4ssw0rd")
```

### Getting logarun data

`get_date_range` takes two positional arguments (`start_date` and `end_date`) and some keyword arguments. It returns an [APIDateRangeResponse object](https://github.com/jflaboe/LogarunExporter/blob/main/logarun.py#L137). The object has a `get_response` attribute to get the actual response.
```
resp = api.get_date_range("05/20/2019", "07/20/2019")
print(resp.get_response())
```

Example output:
```
[('07/21/2015', {'title': 'Capture the Flag', 'activities': [{'type': '\nRun\n', 'Distance': '4.00', 'Unit': 'Mile(s)', 'Time': '00:00:00', 'Pace': '', 'Shoes': "NB Zante's 1", 'Avg HR': '0.0'}, {'type': '\nRun\n', 'Distance': '2.87', 'Unit': 'Mile(s)', 'Time': '00:00:00', 'Pace': '', 'Shoes': "NB Zante's 1", 'Avg HR': '0.0'}]}), ('11/18/2015', {}), ('09/11/2015', {'title': 'Peoria Pre-Meet', 'activities': [{'type': '\nRun\n', 'Distance': '3.00', 'Unit': 'Mile(s)', 'Time': '00:00:00', 'Pace': '', 'Shoes': 'NB vaZEE', 'Avg HR': '0.0'}, {'type': '\nRun\n', 'Distance': '2.00', 'Unit': 'Mile(s)', 'Time': '00:00:00', 'Pace': '', 'Shoes': 'NB vaZEE', 'Avg HR': '0.0'}]}), ('07/23/2015', {'title': 'Copied Toby', 'activities': [{'type': '\nRun\n', 'Distance': '6.00', 'Unit': 'Mile(s)', 'Time': '00:00:00', 'Pace': '', 'Shoes': "NB Zante's 1", 'Avg HR': '0.0'}]}), ('06/14/2015', {'title': 'First Long Run', 'activities': [{'type': '\nRun\n', 'Distance': '9.40', 'Unit': 'Mile(s)', 'Time': '01:04:30', 'Pace': '00:06:51.70 /mile', 'Shoes': "NB Zante's 1", 'Avg HR': '0.0'}]})]
```

### Processing response data with callbacks
GET requests to logarun are made by worker threads in parallel. The number of worker threads can be set as a keyword parameter (default: 10)

```
api = logarun.API(username="jflaboe", workers=20)
```

These workers will fetch one date at a time. You can pass a callback to `get_date_range` to process a single daily value as it gets added to the response. This callback is applied synchronously per worker thread, so if don't want to slow down the API, make your callback create a new thread to do your additional processing.
```
def do_processing(value):
    print(value)
    # do something here
    # no return value needed
     
resp = api.get_date_range("05/20/2019", "07/20/2019", on_add=do_processing)
```

There are also functions to measure the progress of the `get_date_range` response, since it can take a long time. They can be used if you make the function call non-blocking, shown below:
```
import time
import logarun

api = logarun.API(username="jflaboe", workers=20)
resp = api.get_date_range("05/20/2019", "07/20/2019", wait_for_completion=False)

# print the percentage of remaining dates to fetch
while resp.is_complete() is False:
    print(resp.get_remaining_pct())
    time.sleep(10)
```

You can find more of the functions [here](https://github.com/jflaboe/LogarunExporter/blob/main/logarun.py#L137). Note: don't use functions that modify the object. Stick to read-only methods
