#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.


import sys, os
import csv
import json
import logging, logging.handlers
import httplib
import urlparse
import urllib2
import re


class http:
    
    # start function __init__()
    #
    def __init__(self, logger, usage, config, splunkformat, output):
        self.usage = usage
        self.config = config
        self.logger = logger
        if(splunkformat == None):
            self.splunkformat = True
        else:
            self.splunkformat = splunkformat
        if(output == None):
            self.output = sys.stdout
        else:
            self.output = output
    # end function


    # function readtable(url)
    #
    def readtable(self, url):
    
        #validate the url is an http url.
        parsedurl = urlparse.urlparse(url)
        if((parsedurl.scheme != "https" and parsedurl.scheme != "http")   or parsedurl.netloc.__len__() < 1 or parsedurl.path.__len__() < 1):
            raise Exception("Invalid url:" + url)
        
        #Determine if this is http or https
        protocol = "http"
        if(parsedurl.scheme == "https"):
            protocol = "https"
        
        message = None
        opener = None
        contentlen = None
        try:
            #If a proxy is given try using it.
            (proxyhost, proxyport, proxyuser, proxypass) = self.get_proxyconfig()
            if(proxyhost):
                proxy_info = { "user":proxyuser,"pass":proxypass,"host":proxyhost,"port":long(proxyport)}
                proxy_support = urllib2.ProxyHandler({parsedurl.scheme:parsedurl.scheme+"://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy_info})
                opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
            #otherwise just use standard connection.
            else:
                opener = urllib2.build_opener(urllib2.HTTPHandler)
            
            #open the url and get a file 
            urllib2.install_opener(opener)
            message = urllib2.urlopen(url)
            
            #Determine the content length.
            contentlen = message.headers['Content-Length']
            
            #Make the buffer size 1K
            buffersize = 1000
            if(long(contentlen) <= buffersize):
                buffersize = long(contentlen)
            
            # If this is to be in splunkformat then add the _raw field.
            if(self.splunkformat):
                self.output.write("_raw\n\"")
            
            #Cycle through all the data... writing to stdout 
            totalread = 0
            newlines = True
            while (totalread < long(contentlen)):
                totalread = totalread + buffersize
                buffer = message.read(buffersize)
                
                if(self.splunkformat): 
                    # replace all " with "" this is the formatting needed by splunk.          
                    buffer = re.sub(r"(\")", "\"\"", buffer)
                elif(self.splunkformat == "newlinesep"):
                    buffer = re.sub(r"(\")", "\"\"", buffer)
                    if(re.search(r"(\r\n)", buffer)):
                        buffer = re.sub(r"(\r\n)", "\"\r\n\"", buffer)
                    elif(re.search(r"(\r)", buffer)):
                        buffer = re.sub(r"(\r)", "\"\r\"", buffer)
                    elif(re.search(r"(\n)", buffer)):
                        buffer = re.sub(r"(\n)", "\"\n\"", buffer)
                    else:
                        newlines = False
                        
                    #remove the trailing quote.
                    bufsize = buffer.__len__()
                    if(totalread >= long(contentlen) and newlines):
                        buffer = buffer[0:bufsize-1]
                
                self.output.write(buffer)
                
            
            
            if(self.splunkformat):
                self.output.write("\"")
        
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            if(message != None):
                message.close()
            if(opener != None):
                opener.close()
    # end function      

    # start function
    #
    def get_proxyconfig(self):
        db = self.config
        proxyhost=None
        proxyport=None
        proxyuser=None
        proxypass=None
        

        if(db != None):
            for dbkey in db.keys():
                if(str(dbkey) == "proxyhost"):
                    proxyhost = db[dbkey]
                    self.logger.debug("proxyhost:" + proxyhost)
                if(str(dbkey) == "proxyport"):
                    proxyport = db[dbkey]
                    self.logger.debug("proxyport:" + proxyport)
                if(str(dbkey) == "proxyuser"):
                    proxyuser = db[dbkey]
                    self.logger.debug("proxyuser:" + proxyuser)
                if(str(dbkey) == "proxypass"):
                    proxypass = db[dbkey]
                    self.logger.debug("proxypass:" + proxypass)
        
        return (proxyhost,proxyport,proxyuser,proxypass)
    # end function
    