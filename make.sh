#!/bin/bash

if [ "$SPLUNK_HOME" == "" ]
then
    echo "SPLUNK_HOME must be set."
else
    cp -Rf bin/*.py $SPLUNK_HOME/etc/apps/importutil/bin/
fi
