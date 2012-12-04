#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.


import sys, os
#import splunk
import csv
import json
import subprocess
import logging, logging.handlers
import splunk.Intersplunk
import StringIO
#import splunk.bundle as bundle
#import splunk.clilib.cli_common 
import httplib
import urlparse


class http:
    
    # start function __init__()
    #
    def __init__(self, logger, usage, config):
        self.config = config
        self.logger = logger
    # end function




    # function outputjson()
    # Creates a splunk readable dictionary, where each row has a "_raw" key.
    def outputjson(self, csvrows):
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
    def producerawdict(self, csvrows):
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

        
    # function readtable(url)
    #
    def readtable(self, url):
        #validate the url is an http url.
        parsedurl = urlparse.urlparse(url)
        if(parsedurl.scheme != "http" or parsedurl.netloc.__len__() < 1 or parsedurl.path.__len__() < 1):
            splunk.Intersplunk.parseError("Invalid url:" + url  + usage)
        

        #Call the URL, determine size of csv and content type.
        #isZip = "None"
        try:
            con = httplib.HTTPConnection(parsedurl.netloc)
            con.request("HEAD", parsedurl.path)
            response = con.getresponse()
            self.logger.info(parsedurl.path + " Content-Length=" + response.getheader("Content-Length"))
            if(long(response.getheader("Content-Length")) > 99999):
                raise Exception("CSV to large '" + response.getheader("Content-Length") + "'. Content-Length must be <= 99999KB") 
            #if(response.getheader("Content-Type") == "application/zip"):
                #isZip = "True"
            #elif(response.getheader("Content-Type") == "application/gzip"):
                #isZip = "True"
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            if(con != None):
                con.close()
        
        #If it is a zip file then unzip first
        '''if(isZip):
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
        '''
        
        #Call the URL, get the csv.
        csvrows = None
        con = None
        try:
            con = httplib.HTTPConnection(parsedurl.netloc)
            con.request("GET", parsedurl.path)
            response = con.getresponse()
            csvrows = response.read().split("\n")
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            if(con != None):
                con.close()
        
        if(1 == 1):
            #Create a splunk readable "_raw dictionary"
            results = self.producerawdict(csvrows)   

            #output results to splunk.
            if(results != None):
                splunk.Intersplunk.outputResults(results)
        else:
            #Create a wrapper readable json object
            self.outputjson(self, csvrows)
        

    # end function
      

    # function scp_gettable(url)
    #
    def scp_gettable(self, url):
        raise Exception("SCP Not Yet Implemented")
        #validate the url is an http url.
        if("0" == "1"):
            self.logger.warn("Invalid url " + url)
            splunk.Intersplunk.parseError("Invalid url " + url + usage)
        
        #Call the URL, writing results to..splunk.Intersplunk.outputResults
        results = None
        con = None
        try:
            temp = []
            #con = httplib.HTTPConnection("localhost:8000")
            #con.request("GET", "/nickcities.csv")
            #response = con.getresponse()
        
        except Exception as e:
            self.logger.error(e)
        finally:
            if(con != None):
                con.close()
        
        if(response != None): 
            results = response.read().split("\n")
            #TODO This should be streamed or we are going to have memory issue.
            splunk.Intersplunk.outputResults(results)
    # end function 

    
    
