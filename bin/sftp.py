#!/usr/bin/python

#This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/.


import sys, os
import logging, logging.handlers
import paramiko
import urlparse
import re


class sftp:
    
    # start function __init__()
    #
    def __init__(self, logger, usage, config, splunkformat):
        self.config = config
        self.logger = logger
        self.splunkformat = splunkformat
    # end function

        
    # function readtable(url)
    #
    def readtable(self, url):
        
        ssh = None
        sftp = None
        sftpfile = None
        parsedurl = urlparse.urlparse(url)
        
        (proxyhost,proxyport,splunkformat) = self.get_proxyconfig()
        self.splunkformat = splunkformat
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
            ssh.connect(parsedurl.hostname, username=parsedurl.username, password=parsedurl.password)
            sftp = ssh.open_sftp()
            sftpfile = sftp.open(parsedurl.path)
            
            # Add _raw for json logs
            if(self.splunkformat):
                sys.stdout.write("_raw\n")
            while(1):
                line = sftpfile.readline()
                if(line == ""):
                    break
                else:
                    # replace all \n with "\n"...replace all " with "" this is the formatting needed by splunk for json.
                    if(self.splunkformat):
                        line = re.sub(r"(\")", "\"\"", line) 
                        line = re.sub(r"(\n)", "\"\n", line) 
                        line = re.sub(r"(\r)", "\"\r", line) 
                        sys.stdout.write("\"" + line )
                    #CSV does not require the quotes or _raw
                    else:
                        sys.stdout.write(line)


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
      