#!/usr/bin/python

import os,re,calendar,datetime,sys
 
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


