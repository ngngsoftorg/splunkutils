#!/usr/bin/python
import sys, os
import StringIO

#print 'Hello World'
results = []
row1 = {"_raw":"asdf"}
row1["_raw"] = "city=tampa,state=florida"
row1["_time"] = "1258387758164372"
results.append(row1)
#print row1;

row2 = {"_raw":"asdf"}
row2['_raw'] = "city=miami,state=florida"
row2['_time'] = "125838775856437"
results.append(row2)

print "[{\"_raw\":\"city=miami,state=florida\",\"_time\":\"1258387758164372\"},"
print "{\"_raw\":\"city=miami,state=florida\",\"_time\":\"1258387758164372\"}]"
#sys.stdout.write(results) 

#splunk.Intersplunk.outputResults(results)
