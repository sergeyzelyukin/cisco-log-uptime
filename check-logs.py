#!/usr/bin/python

import os,re,calendar,datetime,sys
 
class LogLine(dict):  # line in log file, splitted to columns
  months_names = {}
  
  def __init__(self, _line, *year):
    self._ok = True
    
    if len(LogLine.months_names)==0:    
      for _month_num, _month_name in enumerate(calendar.month_abbr):
        LogLine.months_names[_month_name] = _month_num 
      
    if year:
      self._year = year[0]
    else:
      self._year = datetime.datetime.now().year
      
    _pattern = re.compile("^([a-zA-Z]+)\s+([0-9]+)\s+([0-9]+)\:([0-9]+)\:([0-9]+)\s+([a-zA-Z0-9\.\-]+)\s+")
    _m = _pattern.search(_line)
    if _m:
      super(LogLine,self).__setitem__("hostname", _m.group(6))
      try:
        super(LogLine,self).__setitem__("datetime", datetime.datetime.strptime('{0} {1} {2} {3}:{4}:{5}'.format(LogLine.months_names[_m.group(1)],  _m.group(2), str(self._year), _m.group(3), _m.group(4), _m.group(5)), "%m %d %Y %H:%M:%S"))
      except Exception as e:
        self._ok = False
        return
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
    pass
      
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
 


class CatReboots(dict):
  def __init__(self):
    super(CatReboots,self).__init__()
  @staticmethod
  def top_reboots_sort_disc(_item_tuple):
    return len(_item_tuple[-1])
  def top_reboots(self, top=10, max_to_min=True):
    return sorted(self.items(), key=self.top_reboots_sort_disc, reverse=max_to_min)[:top]
  def add(self, _hostname, _datetime):
    if not _hostname in self.keys():
      self.__setitem__(_hostname, [])
    self.__setitem__(_hostname, self.__getitem__(_hostname)+[_datetime])



now = datetime.datetime.now()
cat_reboots = CatReboots()
with os.popen("cat /var/log/cisco/domonet-catalysts-restarts.log") as fh:
  for line in fh:
    logline = LogLine(line.strip())
    if not logline.ok: continue
    if logline.is_reboot():
      if now - logline.datetime<datetime.timedelta(days=30):
        cat_reboots.add(logline.hostname, logline.datetime)

top_reboots = cat_reboots.top_reboots(top=10)

cat_fmt = {}
for hostname,reboots in top_reboots:
  reboots_count = len(reboots)
  if not reboots_count in cat_fmt.keys():
    cat_fmt[reboots_count] = []
  cat_fmt[reboots_count].append(hostname)


def top_numbers_sort_disc(_t):
  return _t[0]
for reboots, catalysts in sorted(cat_fmt.items(), key=top_numbers_sort_disc, reverse=True):
  pass
  print "Number of reboots: '{0}'".format(reboots)
  for cat in catalysts:
    print "\t"+cat
  print



