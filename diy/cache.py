# -*- coding:utf-8 -*-
from collections import OrderedDict

class KVCache(OrderedDict):
    
    def __init__(self,cap=100):
        self.cap = cap
        OrderedDict.__init__(self)
    
    def __setitem__(self,key,value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self,key,value)
        if len(self) > 100:
            first_key = self.keys()
            del self[first_key]
    
