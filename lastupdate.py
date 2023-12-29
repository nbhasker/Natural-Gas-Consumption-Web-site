## Script to send email via the IFTTT Webhooks service with the time of the latest gas monitor update
# Thingspeak and IFTTT identifiers and API keys (TS_CHANNEL, TS_READ_API_KEY, IFTTT_EVENT, 
# IFTTT_API_KEY and LAST_UPDATE_LOG_FILE_NAME) are in lastupdatesecrets.py
# So this script must be run from the same directory as lastupdatesecrets.py

import sys
import requests
import logging
from datetime import datetime, timezone
import dateutil.parser
import urllib.parse

import lastupdatesecrets as l

PROGRAM_NAME = "Gas Monitor Last Update Tracker"
VERSION = 'V0.1'
MAXDELTASECONDS = 1800

# Set exception handler for otherwise unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    raise SystemExit(exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename=l.LAST_UPDATE_LOG_FILE_NAME, filemode='a', format='%(asctime)s - %(levelname)s %(message)s')

logging.info(f"***")
logging.info(f"*** {PROGRAM_NAME} {VERSION} Started ***")

# Retrieve the latest record (JSON formatted) from Thingspeak and extract the ISO format timestamp 
payload = {'api_key': l.TS_READ_API_KEY, 'results': '1'}
r = requests.get(f"https://api.thingspeak.com/channels/{l.TS_CHANNEL}/feeds.json", params=payload)
logging.info(f"Returned url: {r.url}")
d = r.json()
lastupdateisotime = d['feeds'][0]['field1']
logging.info(f"Last update ISO time: {lastupdateisotime}")
# Need dateutil parser as the datetime parser failed to parse these (valid) iso formated timestamps
lastupdatetime = dateutil.parser.isoparse(lastupdateisotime)
logging.info(f"Last update time: {lastupdatetime}")

# datetime needs a timezone to be able to calculate the delta time later
currenttime = datetime.now(timezone.utc)
logging.info(f"Current time: {currenttime}")

deltatime = currenttime - lastupdatetime
deltatimeseconds = deltatime.total_seconds()
logging.info(f"Time difference is {deltatimeseconds} seconds")

# Convert the last update time to a human readable string for display in the IFTTT email
# Note that suppressing the leading zero in the hours field requires a # on Windows (and not a -)
lastupdatetimefmt = lastupdatetime.strftime("%#I:%M:%S %p on %A, %B %e");

# Compose the email subject and body -- the same string is used for both
# The requests module handles urlification of blanks
mailstring = f"Last update was {deltatimeseconds:.0f} seconds ago at {lastupdatetimefmt}"

if (deltatimeseconds <= MAXDELTASECONDS):
    mailstring = f"Gas Logger Status OK - {mailstring}"
else:
    mailstring = f"Check Gas Logger Status - {mailstring}"

logging.info(f"Mail string: {mailstring}")

payload = {'value1': mailstring, 'value2': mailstring}
r = requests.get(f"https://maker.ifttt.com/trigger/{l.IFTTT_EVENT}/with/key/{l.IFTTT_API_KEY}", params=payload)
logging.info(f"Returned url: {r.url}")
logging.info(f"Returned status: {r.status_code}")
logging.info(f"Returned text: {r.text}")

logging.info(f"*** {PROGRAM_NAME} Ended ***")
