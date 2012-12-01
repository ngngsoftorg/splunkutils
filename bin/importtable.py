#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import sqlite3 as lite
import logging, logging.config, logging.handlers
import psycopg2

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


# function - extract_fieldnames
#  extract and return as a list the field names from the given table
#  use the given db type to determine which db to pull from
def extract_fieldnames(type, connectstr, tablename):
    logger.info("extract_fieldnames:type=" + type + ",connectstr=" + connectstr +
         ",tablename=" + tablename)
    if(type == "sqlite"):
        return extract_fieldnames_sqlite(connectstr, tablename)
    elif(type == "postgres"):
        return extract_fieldnames_postgres(connectstr, tablename)
    elif(type == "mysql"):
        return extract_fieldnames_mysql(connectstr, tablename)
    else:
        #This means a user tried an unsupported db
        #TODO - add exception handling
        logger.error("Invalid type " + type)
        raise Exception("Invalid type " + type)
# end function


# function - extract_fieldnames_sqlite
#  extract and retirn as a list the field names from the given table
def extract_fieldnames_sqlite(connectstr, tablename):
    logger.info("extract_fieldnames_sqlite:connectstr=" + connectstr +
                ",tablename=" + tablename)
    con = lite.connect(connectstr)
    
    cur = None
    fieldnames = None
    try:
        cur = con.cursor()  
        cur.execute("PRAGMA table_info(" + tablename + ")")
        description = cur.fetchall()
        
        fieldnames = []
        for row in description:
            fieldnames.append(row[1])
    except Exception as e:
        logger.error(e)
        raise e                
    finally:
        if(cur != None):
            cur.close()
        con.close()
        
    return fieldnames
# end function


# function - extract_fieldnames_postgres
#  extract and retirn as a list the field names from the given table
def extract_fieldnames_postgres(connectstr, tablename):
    logger.info("extract_fieldnames_postgres:connectstr=" + connectstr +
                ",tablename=" + tablename)
    con = psycopg2.connect(connectstr)
    
    #psycopg connections does not support "with" so use traditional try/finally
    cur = None
    fieldnames = None
    try:
        cur = con.cursor()  
        cur.execute("select column_name from information_schema.columns where table_name='" + tablename + "'")
        description = cur.fetchall()
                
        fieldnames = []
        for row in description:
            fieldnames.append(row[0])
        #except:
        #TODO - add exception handling
    except Exception as e:
        logger.error(e)
        raise e                
    finally:
        if(cur != None):
            cur.close()
        con.close()
        
    return fieldnames
# end function


# function - extract_fieldnames_mysql
#  extract and retirn as a list the field names from the given table
def extract_fieldnames_mysql(connectstr, tablename):
    logger.info("extract_fieldnames_mysql:connectstr=" + connectstr +
                ",tablename=" + tablename)
    con = psycopg2.connect(connectstr)
    
    #psycopg connections does not support "with" so use traditional try/finally
    cur = None
    fieldnames = None
    try:
        cur = con.cursor()  
        #What do we do for mysql?
        #cur.execute("select column_name from information_schema.columns where table_name='" + tablename + "'")
        description = cur.fetchall()
        
        fieldnames = []
        for row in description:
            fieldnames.append(row[0])
    #except:
    #TODO - add exception handling
    except Exception as e:
        logger.error(e)
        raise e                
    finally:
        if(cur != None):
            cur.close()
        con.close()
    
    return fieldnames
# end function

# function - select_star
#  select * from the given tablename.
#  Format each row as name=value pairs where the "names" are the given fieldnames.
#  put each row into a json obeject called "_raw"
#  write to stdout as an array of json objects.
def select_star(type, connectstr, tablename, fieldnames):
    logger.info("select_star:type=" + type + ",connectstr=" + connectstr +
                ",tablename=" + tablename + ",fieldnames=")
    con = None
    if(type == "sqlite"):
        con = lite.connect(connectstr)
    elif(type == "postgres"):
        con = psycopg2.connect(connectstr)
    else:
        #This means a user tried an unsupported db
        #TODO - add exception handling
        logger.error("Invalid type " + type)
        raise Exception("Invalid type " + type)
       
            
    #psycopg connections does not support "with" so use traditional try/finally   
    cur = None
    try:
    
        cur = con.cursor() 
        cur.execute("SELECT * FROM " + tablename) 
        rows = cur.fetchall()
    
        length = rows.__len__()
        count = 0
        print "["
        for row in rows:
            count = count + 1 
        
            #create a json row
            fieldCount = 0
            buffer = "{\"_raw\":\""
            numOfFields = row.__len__()
            for field in row:
                buffer = buffer + fieldnames[fieldCount] + "=" + str(field)
                if(fieldCount < numOfFields-1):
                    buffer = buffer + ","
                fieldCount = fieldCount + 1
            buffer = buffer + "\"}"
        
            if(count < length):
                buffer = buffer + ","  
            print buffer
        print "]" 
    except Exception as e:
        logger.error(e)
        raise e      
    finally:
        if(cur != None):
            cur.close()
        con.close()
# end function


# function - usage
#   display how to use this python script
def usage():
    print "\nUsage: importtable.py postgres|sqlite <connectstr> <tablename>\n"
# end function


logger = setup_logging()
logger.info("Init importtable.py")

if(sys.argv.__len__() < 4):
    logger.warn("Invalid arguments")
    usage()
    sys.exit(2)

try:   
    type = sys.argv[1]
    connectstr = sys.argv[2]
    tablename = sys.argv[3]
    fieldnames = extract_fieldnames(type, connectstr, tablename)
    select_star(type, connectstr, tablename, fieldnames)
except Exception as e:
    logger.error(e)
    sys.exit(1)
    
sys.exit(0)



   
   


