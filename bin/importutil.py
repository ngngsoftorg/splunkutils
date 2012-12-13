#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

import sys, os
import logging, logging.handlers
import splunk
import splunk.clilib.cli_common 
import splunk.Intersplunk
import splunk.bundle as bundle
import re

 
def __setup_logging():
    """Sets up logging for importutil"""
    
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
    
    
def usage():
    """Returns usage information for importutil"""
    
    return "\nUsage   : importutil [config=<config>] [format=<format>] <protocol> <url>" + "\nExample : importutil http http://research.stlouisfed.org/fred2/data/PAYEMS.txt"


def __getparams():
    """Determines if params are valid and returns:
    (config, splunkformat, protocol, url)"""
    
    if(sys.argv.__len__() < 3 or sys.argv.__len__() > 5):
        logger.warn("Invalid arguments")
        splunk.Intersplunk.parseError("Invalid arguments - " + usage())
    
    config = None
    splunkformat = None
    protocol = None
    url = None

    if(sys.argv.__len__() == 4):
        if(re.search("config=",sys.argv[1])):
            config = sys.argv[1]["config=".__len__():]
        elif(re.search("format",sys.argv[1])):
            splunkformat = True
        else:
            logger.warn("Invalid arguments")
            splunk.Intersplunk.parseError("Invalid arguments - " + usage())  
        protocol = sys.argv[2]
        url = sys.argv[3]
    elif(sys.argv.__len__() == 5):
        if(re.search("config=",sys.argv[1]) and re.search("format",sys.argv[2])):
            config = sys.argv[1]["config=".__len__():]
            splunkformat = True
            protocol = sys.argv[3]
            url = sys.argv[4]
        else:
            logger.warn("Invalid arguments")
            splunk.Intersplunk.parseError("Invalid arguments - " + usage())  
    else:   
        protocol = sys.argv[1]
        url = sys.argv[2]
        
    return (config, splunkformat, protocol, url) 



logger = __setup_logging()
    
(config, splunkformat, protocol, url) = __getparams()

try:
    if(config):
        config = splunk.clilib.cli_common.getMergedConf('importutil')[config]
    # invoking in this manner allows for polymorphism.  Anyone can implement a new protocol as long as the protocol.protocol.__init__(logger, usage) and protocol.protocol.readtable(url) methods exist
    module = __import__(protocol)
    instance = getattr(module, protocol)(logger, usage(), config, splunkformat)
    instance.readtable(url)   
    
    #else:
    #logger.warn("Invalid protocol " + protocol)
    #   splunk.Intersplunk.parseError("Invalid protocol " + protocol + " - " + usage())
except Exception as e:
    logger.error(e)
    splunk.Intersplunk.parseError(str(e) + usage())


    
