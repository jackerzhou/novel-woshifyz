# -*- coding:utf-8 -*-

class KVCache(object):
    
    def __init__(self,cap=100):
        self.cap = cap
        self._count = 0
        self.data = {}
        self.key_stack = []
    
    def get(self,key):
        return self.data.get(key,None)
        
    def set(self,key,value):
        self.data[key] = value
        if key in self.key_stack:
            self.key_stack.remove(key)
        else:
            self._count += 1
        self.key_stack.append(key)
        if self._count >= self.cap:
            self.key_stack.remove(self.key_stack[0])

    def delete(self,key):
        try:
            del self.data[key]
            self.key_stack.remove(key)
            self._count -= 1
        except KeyError:
            pass
    
