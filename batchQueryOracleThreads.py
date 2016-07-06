# File: batchQueryOracle.py
# Author: John B Damask
# Created: January 25, 2016
# Purpose: Generic script to excute sql statements from user-provided file and print comma-delimited results to STDOUT
# Synopsis: python oracle.py scratch blah.sql > data.csv
# Notes: User must have params.py in home directory with db user / pass in the format:
#        mydbUN = 'user'
#        mydbPW = 'pass'
#        mydbHOST = 'hostname'

import cx_Oracle, sys, csv, re
from os.path import expanduser
home = expanduser("~")
sys.path.append(home)
import params
import threading

# Read args
db = sys.argv[1]
sqlFile = sys.argv[2]

# Scrub queries
notAllowed = set(['insert', 'INSERT', 'update', 'UPDATE', 'delete', 'DELETE', 'merge', 'MERGE', 'drop', 'DROP'])

# Connect to database
dbUN = "params."+ db + "UN"
dbPW = "params." + db + "PW"
dbHOST = "params." + db + "HOST"
conStr = "%s/%s@%s"% (eval(dbUN), eval(dbPW), eval(dbHOST))
con = cx_Oracle.connect(conStr, threaded=True)

#subclass of threading.Thread
class AsyncSelect(threading.Thread):
  def __init__(self, cur, sql, outFileName):
    threading.Thread.__init__(self)
    self.cur = cur
    self.sql = sql
    self.outFileName = outFileName
  def run(self):
    #res = self.cur.fetchall()
    self.cur.execute(self.sql)
    outFile = open(str(self.outFileName) + ".csv", 'w')
    outLog = open(str(self.outFileName) + ".log", 'w')
    columns = [i[0] for i in self.cur.description]
    output = csv.writer(outFile, lineterminator='\n', delimiter='|')
    outputLog = csv.writer(outLog, lineterminator='\n', delimiter='|')
    output.writerow(columns)
    #for r in res:
    done = False
    while not done:
      #for r in cur.fetchmany():
      records = self.cur.fetchmany()
      if records == []:
        done = True
      for rec in records:
        it = iter(rec)
        nt = []
        tf = True
        for el in it:
          if isinstance(el, str):
            s1 = el.translate(None, '\r\n"')    # Get rid of non-functional chars that mess up Vertica imports
            s1 = s1.replace('|', ':')           # | is our Vertica field delimiter so substitute : whenever found inside fields
            tf = False if (s1 != el) else tf
          elif isinstance(el, cx_Oracle.LOB):
            s1 = 'LOB field. See original Oracle record'
          else:
            s1 = el
          nt.append(s1)
        output.writerow(tuple(nt))
        outputLog.writerow(rec) if not tf else None
    outFile.close()
    outLog.close()
    self.cur.close()

# Open file containing valid select queries
th = []
with open(sqlFile, 'r') as f:
    outFile = None
    for n, line in enumerate(f):
        words = line.split()
        for word in words:
            if word in notAllowed:
                print ("Disallowed SQL statement...moving to next")
                continue
        try:
            # Added cursor here for multithreading
            cur = con.cursor()
            # Hack to get the name of the first table in the SELECT query
            tblName = re.search('FROM ([^,\s]+)', line).group(1)
            # Remove schema if it exists
            if '.' in tblName:
              tblName = tblName.split('.')[1]              
            # Append index, just in case multiple queries against the same table are in the file
            tblName = tblName + "_" + str(n)
            #th.append(AsyncSelect(cur, line, n))
            th.append(AsyncSelect(cur, line, tblName))
            th[n].start()
        except cx_Oracle.DatabaseError as e:
                error, = e.args
                print ("ERROR", line)
                print(error.code)
                print(error.message)
                print(error.context)

for t in th:
    t.join()
con.close()

