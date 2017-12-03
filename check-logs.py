#!/usr/bin/python

import os,re,calendar,datetime,sys
 
class LogLine(dict):  # line in log file, splitted to columns
  months_names = {}
  
  def __init__(self, _line, *year):
    self._ok = True
    
    if len(LogLine.months_names)==0:    
      for _month_num, _month_name in enumerate(calendar.month_abbr):
        LogLine.months_names[_month_name] = _month_num  # common for all objects
      
    if year:
      self._year = year[0]
    else:
      self._year = datetime.datetime.now().year
      
    _pattern = re.compile("^([a-zA-Z]+)\s+([0-9]+)\s+([0-9]+)\:([0-9]+)\:([0-9]+)\s+([a-zA-Z0-9\.\-]+)\s+")
    _m = _pattern.search(_line)
    if _m:
      super(LogLine,self).__setitem__("hostname", _m.group(6))
      try:
        _datetime = datetime.datetime.strptime('{0} {1} {2} {3}:{4}:{5}'.format(LogLine.months_names[_m.group(1)],  _m.group(2), str(self._year), _m.group(3), _m.group(4), _m.group(5)), "%m %d %Y %H:%M:%S")
      except Exception as e:
        # wrong date
        self._ok = False
        return
      super(LogLine,self).__setitem__("datetime", _datetime)
    else:
      self._ok = False

    _pattern = re.compile(":\s*([\%\_\-a-zA-Z0-9]+)\s*:\s*([^:]+)$") 
    _m = _pattern.search(_line)
    if _m:
      super(LogLine,self).__setitem__("message_type", _m.group(1).strip())
      super(LogLine,self).__setitem__("message", _m.group(2).strip())
    else:
      self._ok = False
      
  def __setitem__(self):
    pass # do not allow direct changes
      
  def is_reboot(self):
    if not self._ok: return False
    _pattern = re.compile("\%SYS-5-RESTART\s*", re.IGNORECASE)
    _m = _pattern.search(self.__getitem__("message_type"))
    return True if _m else False
      
  @property
  def ok(self):
    return self._ok

  @property
  def datetime(self):
    return self.get("datetime")

  @property
  def hostname(self):
    return self.get("hostname")

  @property
  def message_type(self):
    return self.get("message_type")

  @property
  def message(self):
    return self.get("message")
 

class CatalystsReboots(dict): # catalysts with all their reboots
  def __init__(self):
    super(CatalystsReboots,self).__init__()

  @staticmethod
  def sort_disc(_item_tuple):
    return len(_item_tuple[-1])

  def top_reboots_by_name(self, top=10, max_to_min=True):
    return sorted(self.items(), key=self.sort_disc, reverse=max_to_min)[:top]

  def add(self, _hostname, _datetime):
    if not _hostname in self.keys():
      self.__setitem__(_hostname, [])
    self.__setitem__(_hostname, self.__getitem__(_hostname)+[_datetime])


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
  
