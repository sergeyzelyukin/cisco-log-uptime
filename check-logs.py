#!/usr/bin/python

import os,re,calendar,datetime,sys,time,os
from LogLine import LogLine
from CatalystsReboots import CatalystsReboots
 
def main():
  # Get Params
  try:
    log_filename = sys.argv[1]
    last_days_to_analyze = int(sys.argv[2])
    top_restarts = int(sys.argv[3])
  except IndexError as e:
    print "usage: {0} <LOG FILENAME> <LAST DAYS TO ANALYZE> <TOP RESTARTS> [<HOSTNAME REGEXP>]".format(sys.argv[0])
    sys.exit(1)

  try:
    hostname_pattern = re.compile(sys.argv[4], re.IGNORECASE)
  except IndexError as e:
    hostname_pattern = re.compile(".*", re.IGNORECASE)

  now = datetime.datetime.now()

  if not os.path.exists(log_filename):
    print "there is no such file"
    sys.exit(1)

  # Load Statistics
  start = time.time()

  cats_reboots = CatalystsReboots()
  with open(log_filename, "r") as fh:
    for line in fh:
      line = line.strip()
      
      m = hostname_pattern.search(line)
      if not m: continue
            
      logline = LogLine(line)
      if not logline.ok: continue
      
      m = hostname_pattern.search(logline.hostname)
      if not m: continue
      
      if logline.is_reboot():
        if now - logline.datetime<datetime.timedelta(days=last_days_to_analyze):
          cats_reboots.add(logline.hostname, logline.datetime)

  if not len(cats_reboots): sys.exit(0)

  # Save top
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

  stop = time.time()
  print "Time wasted: %.1f seconds"%(stop-start)


if __name__=="__main__":
  if not sys.version_info[0]==2:
    sys.exit("python version is not supported")

  main()
