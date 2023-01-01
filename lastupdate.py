# Script to send email via the IFTTT Webhooks service with the time of the latest gas monitor update
# Thingspeak and IFTTT identifiers and API keys (TS_CHANNEL, TS_READ_API_KEY, IFTTT_EVENT and IFTTT_API_KEY) are in lastupdatesecrets.py
# So this script must be run from the same directory as lastupdatesecrets.py

import requests
from datetime import datetime, timezone
import dateutil.parser
import urllib.parse

import lastupdatesecrets as l

MAXDELTASECONDS = 600

# Retrieve the latest record (JSON formatted) from Thingspeak and extract the ISO format timestamp 
payload = {'api_key': l.TS_READ_API_KEY, 'results': '1'}
r = requests.get(f"https://api.thingspeak.com/channels/{l.TS_CHANNEL}/feeds.json", params=payload)
print(r.url)
d = r.json()
lastupdateisotime = d['feeds'][0]['field1']
print(lastupdateisotime)
# Need dateutil parser as the datetime parser failed to parse these (valid) iso formated timestamps
lastupdatetime = dateutil.parser.isoparse(lastupdateisotime)
print(lastupdatetime)

# datetime needs a timezone to be able to calculate the delta time later
currenttime = datetime.now(timezone.utc)
print(currenttime)

deltatime = currenttime - lastupdatetime
deltatimeseconds = deltatime.total_seconds()
print(f"Time difference is {deltatimeseconds} seconds")

# Convert the last update time to a human readable string for display in the IFTTT email
# Note that suppressing the leading zero in the hours field requires a # on Windows (and not a -)
lastupdatetimefmt = lastupdatetime.strftime("%#I:%M:%S %p on %A, %B %e");

# Compose the email subject and body -- the same string is used for both
# The requests module handles urlification of blanks
mailstring = f"Last Gas Logger update was {deltatimeseconds:.0f} seconds ago at {lastupdatetimefmt}"

if (deltatimeseconds <= MAXDELTASECONDS):
    mailstring = f"Status OK - {mailstring}"
else:
    mailstring = f"Check Status - {mailstring}"

print(mailstring)

payload = {'value1': mailstring, 'value2': mailstring}
r = requests.get(f"https://maker.ifttt.com/trigger/{l.IFTTT_EVENT}/with/key/{l.IFTTT_API_KEY}", params=payload)
print(r.url)
print(r.status_code)
print(r.text)
