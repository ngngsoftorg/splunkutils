#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

import sys, os
import splunk
import csv
import json
import subprocess
import logging, logging.handlers
import splunk.Intersplunk
import StringIO
import splunk.bundle as bundle
import splunk.clilib.cli_common 
import configuration


# start function setup_logging()
#
def setup_logging():
    logger = logging.getLogger('importtable_wrapper')    
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "importtable_wrapper.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger
# end function

    
# function - usage
#   display how to use this python script
def usage():
    print "\nUsage: importtable_wrapper.py <conf> <url|tablename>\n"
# end function

    
logger = setup_logging()

if(sys.argv.__len__() < 3):
    logger.warn("Invalid arguments")
    usage()
    sys.exit(2)

conf = sys.argv[1]
configdict = splunk.clilib.cli_common.getMergedConf('dbs')
    

#Get configuration 
(type, connectstr) = configuration.get_type_connectstr(configdict, conf)
if(type == None):
    logger.error("No type for configuration: \"" +  conf + "\"")
    raise Exception("No type for configuration: \"" +  conf + "\"")
if(connectstr == None):
    logger.error("No connectstr for configuration: \"" +  conf + "\"")
    raise Exception("No connectstr for configuration: \"" +  conf + "\"")
    
#invoke the subprocess
my_prog = os.path.join(sys.path[0],'importtable.py')
del os.environ['PYTHONPATH']
logger.info("Calling subprocess.Popen(importtable)")
p = subprocess.Popen([my_prog, type, str(connectstr), sys.argv[2]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

output = p.communicate()[0]

# convert stdout buffer object to StringIO object
f = StringIO.StringIO(output)

#Convert StringIO to string
contents = f.getvalue()

# convert string to json object
jsonobj = json.loads(contents)

# Add json object to the Results array 
results = []
for entry in jsonobj:
    results.append(entry)

#print results

#logger.info("Calling splunk.Intersplunk.outputResults")
splunk.Intersplunk.outputResults(results)
