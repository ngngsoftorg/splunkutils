#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

import sys, os
import logging, logging.handlers
import StringIO


# start function setup_logging()
#
def setup_logging():
    logging.basicConfig(
                        filename='importtable.log',level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger('importtable')
    #splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger
# end function

# start function
#
def get_type_connectstr(configdict, configuration):
    type=None
    connectstr=None
    
    for configkey in configdict.keys():
        #Get the db configuration specified in the search command
        if(str(configkey) == configuration):
            #First, determine which db type (e.g. postgres, mysql, sqlite) the configuration specifies. 
            db = configdict[configkey]
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
    