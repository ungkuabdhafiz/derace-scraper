# Derace Scraper

Scrape data from derace.com using Playwright.

All the data about the horses and races are being fetched from a websocket endpoint. This websocket endpoint is generated uniquely for each page visit and therefore make it hard to connect to the websocket directly from outside of the browser environment. That is the reason why Playwright is being used. Not an ideal solutions but good enough to get the data for further processing.

There are 4 main data we are getting here denoted by each url. The horse url provides detailed information for each horse. The horses url provides brief information for horses on display for each page. The races url provides the latest information for the recent races or upcoming races. The races/results url provides historical races data.

You may need to edit the MAX_HORSE_PAGE, MAX_RACES_PAGE and HORSE_COUNT variables depends on when you run this code.

The data folders will contain three folders: horse, horses, races. current_race.json is the output from races url. The number in horse folder represents data for each horse. The number in horses and races folders represent the page number.

Ideally, you want to process the json data after the process has finished by inserting the data into a database. You may need to run this process several times to cover for data losses due to exceptions and connection problems. For example, you may encounter the *Timeout 30000.0ms exceeded while waiting for event "websocket"* error from time to time.

The wait_for_timeout syntax scattered around the code is needed there to allow for the page to load completely and for the websocket data to be fetched. Feel free to fork and provide better suggestions and improvements.


## Usage

Usage is pretty straightforward, create a virtual environment and install all the dependencies required.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

and run the code

```
python derace_scraper.py
```

All the output data will be stored in data folder.
