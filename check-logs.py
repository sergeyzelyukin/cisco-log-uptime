#!/usr/bin/python

import os,re,calendar,datetime,sys,xlsxwriter
from LogLine import LogLine
from CatalystsReboots import CatalystsReboots
 
def main():
  # Get Params
  try:
    log_filename = sys.argv[1]
    last_days_to_analyze = int(sys.argv[2])
    top_restarts = int(sys.argv[3])
  except IndexError as e:
    print "usage: check-logs.py <LOG FILENAME> <LAST DAYS TO ANALYZE> <TOP RESTARTS> [<HOSTNAME REGEXP>]"
    sys.exit()
  
  try:
    hostname_pattern = re.compile(sys.argv[4])
  except IndexError as e:
    hostname_pattern = re.compile(".*")

  now = datetime.datetime.now()

  # Load Statistics
  cats_reboots = CatalystsReboots()
  with open(log_filename, "r") as fh:
    for line in fh:
      logline = LogLine(line.strip())
      if not logline.ok: continue
      
      m = hostname_pattern.search(logline.hostname)
      if not m: continue
      
      if logline.is_reboot():
        if now - logline.datetime<datetime.timedelta(days=last_days_to_analyze):
          cats_reboots.add(logline.hostname, logline.datetime)

  if not len(cats_reboots): sys.exit(0)

  # Save top
  top_reboots = cats_reboots.top_reboots_by_name(top=top_restarts)

  #workbook = xlsxwriter.Workbook('%s.xlsx'%(sys.argv[0]))
  #worksheet = workbook.add_worksheet()
  
  hostname, reboots = top_reboots.pop(0)
  reboots_count = len(reboots)
  new_value = True
  #row = 1
  while len(top_reboots):
    if new_value:
      print "Number of reboots: %d"%(reboots_count)
      #worksheet.write("A%d"%(row), "Number of reboots: %d"%(reboots_count))
      #row += 1
    print "\t{0}".format(hostname)
    #row += 1
    #worksheet.write("A%d"%(row), "\t{0}".format(hostname))
    hostname, reboots = top_reboots.pop(0)    
    if not len(reboots)==reboots_count:
      reboots_count = len(reboots)
      new_value = True  
    else:
      new_value = False

  #workbook.close()


if __name__=="__main__":
  main()
  
