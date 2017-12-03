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
 

