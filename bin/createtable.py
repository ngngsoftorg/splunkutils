#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys


# function - create
def create():
    con = lite.connect('test.db')
    with con:
        cur = con.cursor()    
        cur.execute("CREATE TABLE eaglecities(Id INT, City TEXT, State TEXT)")
        cur.execute("INSERT INTO eaglecities VALUES(1, 'Bloomington', 'Indiana')")
        cur.execute("INSERT INTO eaglecities VALUES(2, 'Cincinnati', 'Ohio')")
        cur.execute("INSERT INTO eaglecities VALUES(3, 'Chicago', 'Illinois')")
        cur.execute("INSERT INTO eaglecities VALUES(4, 'San Francisco', 'California')")
# end function

# function - usage
#   display how to use this python script
def usage():
    print "Usage: creattable.py"
# end function


try:   
    create()
except:
    sys.exit(1)
    
sys.exit(0)

    


