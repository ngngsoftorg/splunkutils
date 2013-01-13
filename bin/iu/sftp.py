#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.


import sys, os
import logging, logging.handlers
import paramiko
import urlparse
import re


class sftp:
    
    def __init__(self, logger, usage, config, splunkformat, output):
        """
        sftp constructor.
        @param logger - must be a valid logger object.  Where sftp writes its logs.
        @param usage - a method which describes usage of the system.
        @param config - NOT YET IMPLEMENTED, BUT REQUIRED
        A dictionary containing proxy config info.  proxyhost and proxyport, currently pro
        @param splunkformat - NOT YET IMPLEMENTED, BUT REQUIRED.
        Will write url in single splunk event format  : _raw "event 1, event 2" to stdout.
        """
        self.config = config
        self.logger = logger
        if(splunkformat == None):
            self.splunkformat = "raw"
        else:
            self.splunkformat = splunkformat
        if(output == None):
            self.output = sys.stdout
        else:
            self.output = output



    def readtable(self, url):
        """
        Public method
        Get's the data from the file at the given sftp URL.
        Writes the data to stdout using the splunk _raw single event format:
        _raw
        "event 1
        event 2
        event 3"
        """
        ssh = None
        sftp = None
        sftpfile = None
        parsedurl = urlparse.urlparse(url)
        
        (proxyhost,proxyport,proxyuser,proxypass) = self.__get_proxyconfig()
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
            ssh.connect(parsedurl.hostname, username=parsedurl.username, password=parsedurl.password)
            sftp = ssh.open_sftp()
            sftpfile = sftp.open(parsedurl.path)
            
            # Add _raw for json logs
            if(self.splunkformat == "raw"):
                #self.output.write("_raw\n")
                self.output.write("_raw\n\"")
                
            while(1):
                line = sftpfile.readline()
                if(line == ""):
                    break
                else:
                    
                    if(self.splunkformat == "raw"):
                        line = re.sub(r"(\")", "\"\"", line) 
                        # replace all \n with "\n"...replace all " with "" this is the formatting needed by splunk for json.
                        #line = re.sub(r"(\n)", "\"\n", line) 
                        #line = re.sub(r"(\r)", "\"\r", line) 
                        #self.output.write("\"" + line )
                        self.output.write(line)
                    #CSV does not require the quotes or _raw
                    else:
                        self.output.write(line)
                            
            if(self.splunkformat == "raw"):
                self.output.write("\"")


        except Exception as e:
            self.logger.error(e)
            raise e
        finally:
            if(sftpfile != None):
                sftpfile.close()
            if(sftp != None):
                sftp.close()
            if(ssh != None):
                ssh.close()


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
      