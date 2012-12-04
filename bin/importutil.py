#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.


import sys, os
import logging, logging.handlers
import splunk
import splunk.clilib.cli_common 
import splunk.Intersplunk

#import splunk.bundle as bundle

 
    
# start function setup_logging()
#
def setup_logging():
    logger = logging.getLogger('importutil')    
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "importutil.log"
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
    return "\nUsage   : importutil <protocol> <url> [<datasource-stanza>]" + "\nExample : importutil http http://localhost/some/example.csv httpproxyconfig"
# end function

logger = setup_logging()

if(sys.argv.__len__() < 3):
    logger.warn("Invalid arguments")
    splunk.Intersplunk.parseError("Invalid arguments - " + usage())
    
protocol = sys.argv[1]
url = sys.argv[2]
datasource = None
    

try:

    if(sys.argv.__len__() == 4):
        datasource = splunk.clilib.cli_common.getMergedConf('dbs')[sys.argv[3]]
    # invoking in this manner allows for polymorphism.  Anyone can implement a new protocol as long as the protocol.protocol.__init__(logger, usage) and protocol.protocol.readtable(url) methods exist
    module = __import__(protocol)
    instance = getattr(module, protocol)(logger, usage(), datasource)
    instance.readtable(url)   
    
    #else:
    #logger.warn("Invalid protocol " + protocol)
    #   splunk.Intersplunk.parseError("Invalid protocol " + protocol + " - " + usage())
except Exception as e:
    logger.error(e)
    splunk.Intersplunk.parseError(str(e) + usage())


    
