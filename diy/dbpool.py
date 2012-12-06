from tornado.database import Connection
import random
from threading import RLock

class DBPool(object):

    def __init__(self,min_conn=3,max_conn=10,*argv,**kw):
        self.max_conn = max_conn
        self.min_conn = min_conn
        self._conn_pool = []
        self._shared_pool = []
        self._rlock = RLock()
        self._conn_num = 0
        self._idle_num = 0
        self._argv = argv
        self._kw = kw
        self.__init_start_conn()

    def __init_start_conn(self):
        self._rlock.acquire()
        for i in range(self.min_conn):
            _conn = Connection(*self._argv,**self._kw)
            self._conn_pool.append(_conn)
            self._conn_num += 1
            self._idle_num += 1

        self._rlock.release()

    def connect(self):
        self._rlock.acquire()
        res = None
        if self._idle_num:
            res = self._conn_pool.pop(0)
            self._idle_num -= 1
            self._shared_pool.append(res)

        else:
            if self._conn_num >= self.max_conn:
                _r_num = random.randint(0,len(self._shared_pool)-1)
                res = self._shared_pool[_r_num]

            else:
                _conn = Connection(*self._argv,**self._kw)
                self._shared_pool.append(_conn)
                self._conn_num += 1
                res = _conn
        self._rlock.release()
        return res

    def close(self):
        self._rlock.acquire()
        for _conn in self._conn_pool:
            try:
                _conn.close()
                self._conn_num -= 1
                self._idle_num -= 1
            except:
                print 'close connection error'

        for _conn in self._shared_pool:
            try:
                _conn.close()
                self._conn_num -= 1
            except:
                print 'close connection error'
        self._rlock.release()

    
    def __del__(self):
        self.close()
