#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.


import sys, os
import logging, logging.handlers
import ftplib
import re
import urlparse
import urllib2

class ftp:
    
    # start function __init__()
    #
    def __init__(self, logger, usage, config, splunkformat):
        self.config = config
        self.logger = logger
        self.splunkformat = splunkformat
        self.filesize = 0
        self.totalread = 0
    # end function

        
    # function readtable(url)
    #
    def readtable(self, url):
        
        ftp = None
        buffersize = 0
        parsedurl = urlparse.urlparse(url)
        
        (proxyhost,proxyport,splunkformat) = self.get_proxyconfig()
        self.splunkformat = splunkformat
        
        try:
            ftp = ftplib.FTP(parsedurl.hostname)
            ftp.login(parsedurl.username, parsedurl.password)
            
            #Set to binary.
            ftp.sendcmd("TYPE i")
            #Determine file size.
            self.filesize = ftp.size(parsedurl.path) 
            # Add _raw for json logs
            if(self.splunkformat):
                sys.stdout.write("_raw\n\"")
            #Get the data.
            ftp.retrbinary('RETR ' + parsedurl.path, self.__handleDownload)
            
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            if(ftp != None):
                ftp.quit()
        
    # end function


    # start function __handleDownload()
    #     
    def __handleDownload(self, buffer):     
        self.totalread = self.totalread + buffer.__len__()   
        newlines = True
        
        # replace all \n with "\n"...replace all " with "" this is the formatting needed by splunk for json.
        if(self.splunkformat):
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
            if(self.totalread == self.filesize and newlines):
                buffer = buffer[0:bufsize-1]        
        
        sys.stdout.write(buffer)
    # end function
    
    
    
    # start function
    #
    def get_proxyconfig(self):
        db = self.config
        proxyhost=None
        proxyport=None
        splunkformat = self.splunkformat
        
        
        if(db != None):
            for dbkey in db.keys():
                if(str(dbkey) == "proxyhost"):
                    proxyhost = db[dbkey]
                    self.logger.trace("proxyhost:" + proxyhost)
                if(str(dbkey) == "proxyport"):
                    proxyport = db[dbkey]
                    self.logger.trace("proxyport:" + proxyport)
        
        return (proxyhost,proxyport,splunkformat)
    # end function

    
