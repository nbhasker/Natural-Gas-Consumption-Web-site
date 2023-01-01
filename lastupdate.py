import requests
from datetime import datetime, timezone
import dateutil.parser
import urllib.parse
import lastupdatesecrets as l

MAXDELTASECONDS = 600

payload = {'api_key': l.TS_READ_API_KEY, 'results': '1'}
r = requests.get(f"https://api.thingspeak.com/channels/{l.TS_CHANNEL}/feeds.json", params=payload)
print(r.url)
d = r.json()
lastupdateisotime = d['feeds'][0]['field1']
print(lastupdateisotime)
lastupdatetime = dateutil.parser.isoparse(lastupdateisotime)
print(lastupdatetime)

currenttime = datetime.now(timezone.utc)
print(currenttime)

deltatime = currenttime - lastupdatetime
deltatimeseconds = deltatime.total_seconds()
print(f"Time difference is {deltatimeseconds} seconds")

lastupdatetimefmt = lastupdatetime.strftime("%#I:%M:%S %p on %A, %B %e");

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
