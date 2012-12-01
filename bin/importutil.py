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
import httplib
import urlparse


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


# function outputjson()
# Creates a splunk readable dictionary, where each row has a "_raw" key.
def outputjson(csvrows):
    header = "True"
    headervalues = None
    numoffields = 0
    results = []
    reader = csv.reader(csvrows)
    
    #if first line is header then pull it out.
    if(header):
        for row in reader:
            #pull out the header values
            headervalues = row
            #determine number of fields
            numoffields = row.__len__()
            break
            
    numofrows = csvrows.__len__()
    currentrow = 0
    print "["
    #Add rows to the result object.
    for row in reader:
        
        #Stop if you hit an empty line 
        if(row.__len__() == 0):
            break
        
        buffer = ""
        i = 0
        for field in row:
            buffer = buffer + headervalues[i] + "=" + field
            if(i < numoffields-1):
                buffer = buffer + ","                
            i = i + 1
        
        buffer =  "{\"_raw\":\"" + buffer + "\"}"
        if(currentrow < numofrows - 1):
            buffer = buffer + ","
        
        print buffer
        currentrow = currentrow + 1
    print "]"
# end function
    

# function producerawdict()
# Creates a splunk readable dictionary, where each row has a "_raw" key.
def producerawdict(csvrows):
    header = "True"
    headervalues = None
    numoffields = 0
    results = []
    reader = csv.reader(csvrows)
    
    #if first line is header then pull it out.
    if(header):
        for row in reader:
            #pull out the header values
            headervalues = row
            #determine number of fields
            numoffields = row.__len__()
            break
    
    #Add rows to the result object.
    for row in reader:
        
        #Stop if you hit an empty line 
        if(row.__len__() == 0):
            break
        
        newrow = ""
        i = 0
        for field in row:
            newrow = newrow + headervalues[i] + "=" + field
            if(i < numoffields-1):
                newrow = newrow + ","                
            i = i + 1
        
        results.append({ '_raw':newrow})
    return results
# end function

    
# function http_gettable(url)
#
def http_gettable(url):
    #validate the url is an http url.
    parsedurl = urlparse.urlparse(url)
    if(parsedurl.scheme != "http" or parsedurl.netloc.__len__() < 1 or parsedurl.path.__len__() < 1):
        splunk.Intersplunk.parseError("Invalid url:" + url  + usage())
    

    #Call the URL, determine size of csv.
    try:
        con = httplib.HTTPConnection(parsedurl.netloc)
        con.request("HEAD", parsedurl.path)
        response = con.getresponse()
        logger.info(parsedurl.path + " Content-Length=" + response.getheader("Content-Length"))
        if(long(response.getheader("Content-Length")) > 99999):
            raise Exception("CSV to large. Content-Length must be <= 99999KB") 
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        if(con != None):
            con.close()
            

    #Call the URL, get the csv.
    csvrows = None
    con = None
    try:
        con = httplib.HTTPConnection(parsedurl.netloc)
        con.request("GET", parsedurl.path)
        response = con.getresponse()
        csvrows = response.read().split("\n")
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        if(con != None):
            con.close()
    
    if(0 == 1):
        #Create a splunk readable "_raw dictionary"
        results = producerawdict(csvrows)   

        #output results to splunk.
        if(results != None):
            splunk.Intersplunk.outputResults(results)
    else:
        #Create a wrapper readable json object
        outputjson(csvrows)
    

# end function
  

# function scp_gettable(url)
#
def scp_gettable(url):
    raise Exception("SCP Not Yet Implemented")
    #validate the url is an http url.
    if("0" == "1"):
        logger.warn("Invalid url " + url)
        splunk.Intersplunk.parseError("Invalid url " + url + usage())
    
    #Call the URL, writing results to..splunk.Intersplunk.outputResults
    results = None
    con = None
    try:
        temp = []
        #con = httplib.HTTPConnection("localhost:8000")
        #con.request("GET", "/nickcities.csv")
        #response = con.getresponse()
    
    except Exception as e:
        logger.error(e)
    finally:
        if(con != None):
            con.close()
    
    if(response != None): 
        results = response.read().split("\n")
        #TODO This should be streamed or we are going to have memory issue.
        splunk.Intersplunk.outputResults(results)
# end function 

     
# function - usage
#   display how to use this python script
def usage():
    return "\nUsage   : importutil <protocol> <url>" + "\nExample : importutil http http://localhost/some/example.csv"
# end function
    
logger = setup_logging()

if(sys.argv.__len__() < 3):
    logger.warn("Invalid arguments")
    splunk.Intersplunk.parseError("Invalid arguments - " + usage())

protocol = sys.argv[1]
url = sys.argv[2]

try:
    if(protocol == "http"):
        http_gettable(url)
    elif(protocol == "scp"):
        scp_gettable(url)
    else:
        logger.warn("Invalid protocol " + protocol)
        splunk.Intersplunk.parseError("Invalid protocol " + protocol + " - " + usage())
except Exception as e:
    logger.error(e)
    splunk.Intersplunk.parseError(e)
    