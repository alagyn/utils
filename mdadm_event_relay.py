#!/bin/python3
import smtplib

import sys
import datetime
from email.mime.text import MIMEText

event = sys.argv[1]
mdDev = sys.argv[2]
if len(sys.argv) == 4:
    subDev = sys.argv[3]
else:
    subDev = None

remoteServer = "smtp.gmail.com"
remotePort = 465

sendingEmail = None
sendingPass = None
receivingEmail = None

with open("/etc/bdd/raid_relay.env", mode="r") as f:
    for line in f:
        line = line.strip()
        if len(line) == 0 or line.startswith("#"):
            continue
        key, val = line.split('=')
        match key:
            case 'SENDER':
                sendingEmail = val
            case 'PASS':
                sendingPass = val
            case 'RECV':
                receivingEmail = val
            case _:
                pass

if sendingEmail is None or sendingPass is None or receivingEmail is None:
    exit(1)

email = MIMEText(f"An event has been detected\n{event}\n{mdDev}\n{subDev if subDev is not None else ''}")
now = datetime.datetime.now()
email["Subject"] = f'RAID Alert {now.isoformat()}'
try:
    with smtplib.SMTP_SSL(remoteServer, remotePort) as serv:
        serv.login(sendingEmail, sendingPass)
        serv.sendmail(sendingEmail, receivingEmail, email.as_string())
except Exception as e:
    print(e)
