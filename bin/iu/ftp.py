#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.

import sys, os
import logging, logging.handlers
import ftplib
import re
import urlparse
import urllib2


class ftp:
    
    def __init__(self, logger, usage, config, splunkformat, output):
        """
        ftp constructor.
        @param logger - must be a valid logger object.  Where ftp writes its logs.
        @param usage - a method which describes usage of the system.
        @param config - NOT YET IMPLEMENTED, BUT REQUIRED
        A dictionary containing proxy config info.  proxyhost and proxyport, currently pro
        @param splunkformat - NOT YET IMPLEMENTED, BUT REQUIRED.
        Will write url in single splunk event format  : _raw "event 1, event 2" to stdout.
        """
        self.config = config
        self.logger = logger
        if(splunkformat == None):
            self.splunkformat = True
        else:
            self.splunkformat = splunkformat
        self.filesize = 0
        self.totalread = 0
        if(output == None):
            self.output = sys.stdout
        else:
            self.output = output



    def readtable(self, url):
        """
        Public method
        Get's the data from the file at the given ftp URL.
        Writes the data to stdout using the splunk _raw single event format:
            _raw
            "event 1
            event 2
            event 3"
        """
        
        ftp = None
        buffersize = 0
        parsedurl = urlparse.urlparse(url)
        
        (proxyhost,proxyport,proxyuser,proxypass) = self.__get_proxyconfig()
        
        try:
            ftp = ftplib.FTP(parsedurl.hostname)
            ftp.login(parsedurl.username, parsedurl.password)
            
            #Set to binary.
            ftp.sendcmd("TYPE i")
            #Determine file size.
            self.filesize = ftp.size(parsedurl.path) 
            # Add _raw for json logs
            if(self.splunkformat):
                self.output.write("_raw\n\"")
            #Get the data.
            ftp.retrbinary('RETR ' + parsedurl.path, self.__handleDownload)
            
        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            if(ftp != None):
                ftp.quit()


    def __handleDownload(self, buffer):
        """
        Private method.
        A callback funciton used by the ftp.retbinary() method.
        Writes the buffer to stdout.
        Adds a trainling quote if end of the file.
        """
        
        self.totalread = self.totalread + buffer.__len__()   
        newlines = True
        
        if(self.splunkformat):
            buffer = re.sub(r"(\")", "\"\"", buffer)
            # replace all \n with "\n"...replace all " with "" this is the formatting needed by splunk for json.
            """
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
            """
            #add trainling quote
            bufsize = buffer.__len__()
            if(self.totalread == self.filesize):
                buffer = buffer + "\"" 
        
        self.output.write(buffer)


    def __get_proxyconfig(self):
        """
        Private method.
        Returns proxy config for the ftp call.
        """
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
    
