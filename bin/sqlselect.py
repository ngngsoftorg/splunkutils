#!/usr/bin/python
import sqlite3 as lite
import logging
import sys, os
import csv
import splunk.Intersplunk
import StringIO

logger = logging.getLogger("sqlselect")
logger.setLevel(logging.DEBUG)

logger.debug("Hello World")

#results = []

#with con:

#    cur = con.cursor()
#    cur.execute("SELECT * FROM nickscities")
#    rows = cur.fetchall()


#    for row in rows:
#        event = {"_raw":"asdf"}
#        event['_raw'] = row
#        event['_time'] = '1258387758164372' 
#        results.append(event)


#row1['_raw'] = 'city=tampa,state=florida'

#splunk.Intersplunk.outputResults(results)
