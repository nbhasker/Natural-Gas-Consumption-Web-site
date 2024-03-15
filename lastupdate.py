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
import smtplib
from   email.mime.text import MIMEText
from   email.utils import formataddr

import lastupdatesecrets as l

PROGRAM_NAME    = "Gas Monitor Last Update Tracker"
VERSION         = 'V0.2'
MAXDELTASECONDS = 1800

SMTP_SERVER   = 'smtp.gmail.com'
SMTP_TLS_PORT = 587

# Set exception handler for otherwise unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    raise SystemExit(exc_info=(exc_type, exc_value, exc_traceback))

def send_email(subject, body, to_email, from_email, from_name, app_password):
    """
    Send a plaintext email using Gmail's SMTP server with exception handling.

    Parameters:
    - subject: Email subject as a string.
    - body: Email body as a string.
    - to_email: Recipient email address as a string.
    - from_email: Sender's Gmail address as a string.
    - app_password: Sender's Gmail App Password as a string.
    """
    try:
        # Create a plaintext message
        msg            = MIMEText(body)
        msg['Subject'] = subject
        msg['From']    = formataddr((from_name, from_email))
        msg['To']      = to_email

        # Gmail SMTP server setup
        server = smtplib.SMTP(SMTP_SERVER, SMTP_TLS_PORT)
        server.starttls()
        server.login(from_email, app_password)

        # Send email
        server.send_message(msg)
        server.quit()

        logging.info("Email sent successfully!")

    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
    except Exception as e:
        logging.error(f"An error occurred in send_email(): {e}")

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
    mailstring = f"*** Check Gas Logger Status *** - {mailstring}"

logging.info(f"Mail string: {mailstring}")

send_email(
    subject      = mailstring,
    body         = mailstring,
    to_email     = l.GMAIL_TO_EMAIL,
    from_email   = l.GMAIL_FROM_EMAIL,
    from_name    = l.GMAIL_FROM_NAME,
    app_password = l.GMAIL_APP_PASSWORD
)

logging.info(f"*** {PROGRAM_NAME} Ended ***")
