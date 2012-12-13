#!/bin/bash

if [ "$SPLUNK_HOME" == "" ]
then
    echo "SPLUNK_HOME must be set."
else
    cp -Rf bin/* $SPLUNK_HOME/etc/apps/importutil/bin/
    cp -Rf default/* $SPLUNK_HOME/etc/apps/importutil/default/
    cp -Rf metadata/* $SPLUNK_HOME/etc/apps/importutil/metadata/
fi
