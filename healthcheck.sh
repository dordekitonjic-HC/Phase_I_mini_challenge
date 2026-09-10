#!/bin/bash

## Create a cronjob with sudo privileges to run this script. It should be run every minute of the day.


# Calling healtcheck and printing status
status=$(curl -s --connect-timeout 3 "http://192.168.56.13:5000/health" | jq -r '.status')

# Creates backend directory under /var/log/
mkdir -p /var/log/backend/

#This logs the status and sends email to serveradmins if service is down.
if [ "$status" == "ok" ]
then
    echo "["$(date)"]" "["backend status: $status"]" >> /var/log/backend/$(date +"%d-%m-%Y")-backend.log
else
    echo "["$(date)"]" "["backend status: DOWN!"]" >> /var/log/backend/$(date +"%d-%m-%Y")-backend.log
    echo "Backend service is down!" | mail -s "CRITICAL: Backend Down" "admin@serveradmin.com"
fi
