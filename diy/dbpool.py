import tornado.database 
import random
from threading import RLock,Condition

class InvalidConnection(Exception):
    "invalid connection"

class DBPool(object):

    def __init__(self,min_conn=3,max_conn=10,*argv,**kw):
        self.max_conn = max_conn
        self.min_conn = min_conn
        self._conn_pool = []
        self._shared_pool = []
        self._condition = Condition()
        self._conn_num = 0
        self._idle_num = 0
        self._argv = argv
        self._kw = kw
        self.__init_start_conn()

    def __init_start_conn(self):
        self._condition.acquire()
        for i in range(self.min_conn):
            _conn = ConnectionProxy(self,Connection(*self._argv,**self._kw))
            self._conn_pool.append(_conn)
            self._conn_num += 1
            self._idle_num += 1
        self._condition.notify()        
        self._condition.release()

    def connect(self):
        self._condition.acquire()
        res = None
        if self._idle_num:
            res = self._conn_pool.pop(0)
            #print 'return a conn'
            res.ping_check()
            self._idle_num -= 1

        else:
            while self._conn_num >= self.max_conn and self._idle_num <= 0:
                #i don't want to share the connection
                #_r_num = random.randint(0,len(self._shared_pool)-1)
                #res = self._shared_pool[_r_num]
                self._condition.wait()

            else:
                try:
                    res = self._conn_pool.pop(0)
                    self._idle_num -= 1
                    #print 'return a conn'
                    res.ping_check()
                except IndexError:
                    _conn = ConnectionProxy(self,Connection(*self._argv,**self._kw))
                    self._conn_num += 1
                    res = _conn
                    #print 'create a conn'
        self._condition.notify()
        self._condition.release()
        return res

    def close(self):
        self._condition.acquire()
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
        self._condition.notify()
        self._condition.release()

    def cache(self,conn):
        self._condition.acquire()

        self._conn_pool.append(conn)
        #print 'conn back to pool'
        self._idle_num += 1
        self._condition.notify()
        self._condition.release()

    def __del__(self):
        self.close()

class ConnectionProxy(object):
    
    def __init__(self,pool,conn):
        self._conn = conn
        self._pool = pool

    def close(self):
        if self._conn:
            self._pool.cache(self)

    def ping_check(self):
        self._conn.ping_check()

    def __del__(self):
        self.close()

    def __getattr__(self,name):
        if self._conn:
            return getattr(self._conn,name)
        else:
            raise InvalidConnection

class Connection(tornado.database.Connection):
    def __init__(self,ping=1,*args,**kw):
        super(Connection,self).__init__(*args,**kw)
        self._ping = ping
    
    def ping_check(self,ping=1,reconnect=True):
        if self._ping & ping:
            try:
                self._db.ping()
            except (AttributeError, IndexError, TypeError, ValueError):
                self._ping = 0
                return None
            except:
                if reconnect:
                    self.reconnect()
        return True

