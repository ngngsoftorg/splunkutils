#!/usr/bin/python
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

# start function
#
def get_type_connectstr(configuration):
    config = splunk.clilib.cli_common.getMergedConf('dbs')
    type=None
    connectstr=None
    
    logger.info("Retrieve configuration")
    for configkey in config.keys():
        #Get the db configuration specified in the search command
        if(str(configkey) == configuration):
            #First, determine which db type (e.g. postgres, mysql, sqlite) the configuration specifies. 
            db = config[configkey]
            for dbkey in db.keys():
                if(str(dbkey) == "type"):
                    type = db[dbkey]
                    break
            
            #Get the connectstr for sqlite or postgres type
            if(type == "sqlite" or type == "postgres"):
                for dbkey in db.keys():
                    if(str(dbkey) == "connectstr"):
                        connectstr = db[dbkey]
                        break        
            #Get the connectstr oracle type    
            elif(type == "mysql"):
                for dbkey in db.keys():
                    if(str(dbkey) == "connectstr"):
                        connectstr = db[dbkey]
                        break
            break
    
    return (type,connectstr)
# end function
    
# function - usage
#   display how to use this python script
def usage():
    print "\nUsage: importtable_wrapper.py <configuration> <tablename>\n"
# end function
    
logger = setup_logging()

if(sys.argv.__len__() < 3):
    logger.warn("Invalid arguments")
    usage()
    sys.exit(2)

configuration = sys.argv[1]
    

#Get configuration 
(type, connectstr) = get_type_connectstr(configuration)
if(type == None):
    logger.error("No type for configuration: \"" +  configuration + "\"")
    raise Exception("No type for configuration: \"" +  configuration + "\"")
if(connectstr == None):
    logger.error("No connectstr for configuration: \"" +  configuration + "\"")
    raise Exception("No connectstr for configuration: \"" +  configuration + "\"")
    
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

print results

logger.info("Calling splunk.Intersplunk.outputResults")
#splunk.Intersplunk.outputResults(results)
