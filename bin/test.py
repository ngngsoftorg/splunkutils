#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

import sys, os
import logging, logging.handlers
import splunk
import splunk.clilib.cli_common 
import splunk.Intersplunk
import splunk.bundle as bundle
import subprocess
import StringIO
import re
import http
import https
import ftp



# start function setup_logging()
#
def setup_logging():
    logger = logging.getLogger('importutiltest')    
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "importutiltest.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger
# end function

logger = setup_logging()


# Happy path http
output = StringIO.StringIO()
getproto = http.http(logger, "usage", None, "True", output)
getproto.readtable("http://research.stlouisfed.org/fred2/data/PAYEMS.csv")
str_output = output.getvalue()
assert str_output.startswith("_raw"), "Error: Invalid output... \"_raw\" not found."
assert "1991-10-01,108297" in str_output, "Error: Invalid output... \"1991-10-01,108297\" not found in PAYEMS file."
assert str_output.endswith("\""), "Error: Invalid output... does not end in double quote."
print "test: http GET PAYEMS from FRED... returned 200 success"

# Server not found
output = StringIO.StringIO()
getproto = http.http(logger, "usage", None, "True", output)
try:
    getproto.readtable("http://doesnotexist/fred2/data/PAYEMS.csv")
    assert 1 == 1, "Error: Invalid response... should have resulted in Exception due to an unknown server."
except Exception as e:
    logger.warn(e)
    assert "Errno 8" in e.__str__(), "Error: Invalid response... should have resulted in Exception due to an unknown server."
    print "test: http GET PAYEMS from a non existent server... returned Errno 8 success"


# Resource not found
output = StringIO.StringIO()
getproto = http.http(logger, "usage", None, "True", output)
try:
    getproto.readtable("http://research.stlouisfed.org/fred2/data/doesnotexist.csv")
    assert 1 == 1, "Error: Invalid response... should have resulted in HTTP Error 404."
except Exception as e:
    assert "404" in e.__str__(), "Error: Invalid response... should have resulted in HTTP Error 404."
    print "test: http GET a file that does not exist from FRED... returned 404 success"
    


# Happy path https
output = StringIO.StringIO()
getproto = https.https(logger, "usage", None, "True", output)
getproto.readtable("https://research.stlouisfed.org/fred2/data/PAYEMS.csv")
str_output = output.getvalue()
assert str_output.startswith("_raw"), "Error: Invalid output... \"_raw\" not found."
assert "1991-10-01,108297" in str_output, "Error: Invalid output... \"1991-10-01,108297\" not found in PAYEMS file."
assert str_output.endswith("\""), "Error: Invalid output... does not end in double quote."
print "test: https GET PAYEMS from FRED... returned 200 success"


# Server not found
output = StringIO.StringIO()
getproto = https.https(logger, "usage", None, "True", output)
try:
    getproto.readtable("https://doesnotexist/fred2/data/PAYEMS.csv")
    assert 1 == 1, "Error: Invalid response... should have resulted in Exception due to an unknown server."
except Exception as e:
    logger.warn(e)
    assert "Errno 8" in e.__str__(), "Error: Invalid response... should have resulted in Exception due to an unknown server."
    print "test: https GET PAYEMS from a non existent server... returned Errno 8 success"


# Resource not found
output = StringIO.StringIO()
getproto = https.https(logger, "usage", None, "True", output)
try:
    getproto.readtable("https://research.stlouisfed.org/fred2/data/doesnotexist.csv")
    assert 1 == 1, "Error: Invalid response... should have resulted in HTTPS Error 404."
except Exception as e:
    assert "404" in e.__str__(), "Error: Invalid response... should have resulted in HTTPS Error 404."
    print "test: https GET a file that does not exist from FRED... returned 404 success"

# Happy path ftp
output = StringIO.StringIO()
getproto = ftp.ftp(logger, "usage", None, "True", output)
getproto.readtable("ftp://ftp.bls.gov/pub/time.series/ce/ce.data.102.WeeklyEarningsHist")
str_output = output.getvalue()
assert str_output.startswith("_raw"), "Error: Invalid output... \"_raw\" not found."
assert "1991-10-01,108297" in str_output, "Error: Invalid output... \"CEU2000000032    	1973	M08	       12.91\" not found in WeeklyEarningsHist file."
assert str_output.endswith("\""), "Error: Invalid output... does not end in double quote."
print "test: ftp GET WeeklyEarningsHist from bureau of labor... returned 200 success"
    


# Server not found
output = StringIO.StringIO()
getproto = ftp.ftp(logger, "usage", None, "True", output)
try:
    getproto.readtable("ftp://doesnotexist/pub/time.series/ce/ce.data.102.WeeklyEarningsHist")
    assert 1 == 1, "Error: Invalid response... should have resulted in Exception due to an unknown server."
except Exception as e:
    logger.warn(e)
    assert "Errno 8" in e.__str__(), "Error: Invalid response... should have resulted in Exception due to an unknown server."
    print "test: ftp GET WeeklyEarningsHist from a non existent server... returned Errno 8 success"


# Resource not found
output = StringIO.StringIO()
getproto = ftp.ftp(logger, "usage", None, "True", output)
try:
    getproto.readtable("ftp://ftp.bls.gov/pub/time.series/ce/ce.data.102.doesnotexist")
    assert 1 == 1, "Error: Invalid response... should have resulted in ftp Error 550"
except Exception as e:
    assert "550" in e.__str__(), "Error: Invalid response... should have resulted in FTP Error 550."
    print "test: ftp GET a file that does not exist from bureau of labor... returned 550 success"
    