#!/usr/bin/python

import os,re,calendar,datetime,sys
from LogLine import LogLine
from CatalystsReboots import CatalystsReboots
 
def main():
  try:
    log_filename = sys.argv[1]
    last_days_to_analyze = int(sys.argv[2])
    top_restarts = int(sys.argv[3])
  except IndexError as e:
    print "usage: check-logs.py <LOG FILENAME> <LAST DAYS TO ANALYZE> <TOP RESTARTS>"
    sys.exit()

  now = datetime.datetime.now()

  cats_reboots = CatalystsReboots()
  with open(log_filename, "r") as fh:
    for line in fh:
      logline = LogLine(line.strip())
      if logline.is_reboot():
        if now - logline.datetime<datetime.timedelta(days=last_days_to_analyze):
          cats_reboots.add(logline.hostname, logline.datetime)

  if not len(cats_reboots): sys.exit(0)

  top_reboots = cats_reboots.top_reboots_by_name(top=top_restarts)

  hostname, reboots = top_reboots.pop(0)
  reboots_count = len(reboots)
  new_value = True
  while len(top_reboots):
    if new_value:
      print "Number of reboots: %d"%(reboots_count)
    print "\t{0}".format(hostname)
    hostname, reboots = top_reboots.pop(0)    
    if not len(reboots)==reboots_count:
      reboots_count = len(reboots)
      new_value = True  
    else:
      new_value = False




if __name__=="__main__":
  main()
  
