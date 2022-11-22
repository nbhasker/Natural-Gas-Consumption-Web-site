#!/bin/bash
# Script to send email via the IFTTT Webhooks service with the time of the latest gas monitor update
# Thingspeak and IFTTT identifiers and API keys (TS_CHANNEL, TS_READ_API_KEY, IFTTT_EVENT and IFTTT_API_KEY) are in lastupdatesecrets.sh
# So this script must be run from the same directory as lastupdatesecrets.sh

TS_CHANNEL=X
TS_READ_API_KEY=X
IFTTT_EVENT=X
IFTTT_API_KEY=X

source lastupdatesecrets.sh

# Retrieve the latest record (JSON formatted) from Thingspeak, extract the ISO format timestamp 
# and delete the surrounding quotes 
lastupdate=$(curl -s "https://api.thingspeak.com/channels/$TS_CHANNEL/feeds.json?api_key=$TS_READ_API_KEY&results=1" | \
	jq .feeds[0].field1 | tr -d '"')
echo $lastupdate

# Convert the last update time to Unix epoch seconds
lastupdatesecs=$(date -d "$lastupdate" +%s)
echo $lastupdatesecs

# Obtain the current time in Unix epoch seconds
currenttimesecs=$(date +%s)
echo $currenttimesecs

# Calculate the difference in times to see how old the update is
deltasecs=$(($currenttimesecs - $lastupdatesecs))
echo $deltasecs

# Convert the last update time to a human readable string for display in the IFTTT email and urlify
lastupdateurl=$(date -d "$lastupdate" "+%-I:%M:%S %p on %A, %B %e, %Y" | sed -e 's/ /%20/g')
echo $lastupdateurl

# Send the last update time and delta time to the IFTTT webhooks service as value1 and value2 query parameters
curl -s "https://maker.ifttt.com/trigger/$IFTTT_EVENT/with/key/$IFTTT_API_KEY?value1=$lastupdateurl&value2=$deltasecs"

