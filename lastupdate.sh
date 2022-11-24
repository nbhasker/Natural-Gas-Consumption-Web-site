#!/bin/bash
# Script to send email via the IFTTT Webhooks service with the time of the latest gas monitor update
# Thingspeak and IFTTT identifiers and API keys (TS_CHANNEL, TS_READ_API_KEY, IFTTT_EVENT and IFTTT_API_KEY) are in lastupdatesecrets.sh
# So this script must be run from the same directory as lastupdatesecrets.sh

MAXDELTASECS=600

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

# Convert the last update time to a human readable string for display in the IFTTT email
lastupdatefmt=$(date -d "$lastupdate" "+%-I:%M:%S %p on %A, %B %e, %Y")
echo $lastupdateurl

# Compose the email subject and body and urlify -- the same string is used for both
mailstring="Last Gas Logger update was ${deltasecs} seconds ago at ${lastupdatefmt}"

# Prepend status text
if [[ $deltasecs -le $MAXDELTASECS ]]; then
	mailstring="Status OK - ${mailstring}"
else
	mailstring="Check Status - ${mailstring}"
fi

echo $mailstring

mailstringurl=$(echo $mailstring | sed -e 's/ /%20/g')
echo $mailstringurl

# Send the subject and email body to the IFTTT webhooks service as value1 and value2 query parameters
curl -s "https://maker.ifttt.com/trigger/$IFTTT_EVENT/with/key/$IFTTT_API_KEY?value1=$mailstringurl&value2=$mailstringurl"

