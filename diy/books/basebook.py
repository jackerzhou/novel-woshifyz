# -*- coding:utf-8 -*-
from Queue import Queue
import os,os.path
from bs4 import BeautifulSoup
import urllib
import conf

class BaseBook(object):

    #parser list
    def menu_parser(self):
        raise NotImplementedError    

    #parser content of the given url
    def para_parser(self,url):
        raise NotImplementedError

    def gen_one_para_dic(self,para):
        ''' 
            {'source_url':xxx,'title':xxx}
        '''
        raise NotImplementedError
    
    #get the identify num from url
    def gen_url_num(self,url):
        raise NotImplementedError

    #generate link url to openable link
    def make_para_url(self,url):
        return url

    def ensure_table_exist(self):
        query = "create table if not exists %s( " \
                "id int primary key auto_increment, " \
                "num varchar(32) not null default '', " \
                "title varchar(64) not null default '', " \
                "source_url varchar(256) not null default '', " \
                "key num_index(num))engine=innodb,default charset=utf8; " % (self._table_name,)
        self.conn.execute(query)

    def ensure_news_table_exist(self):
        query = "create table if not exists %s( " \
                "id int primary key auto_increment, " \
                "belong varchar(32) not null default '', " \
                "title varchar(128) not null default '', " \
                "num varchar(32) not null default '')engine=innodb,default charset=utf8;" % (conf.NEWS_TABLE_NAME,)
        self.conn.execute(query)

    def gen_last(self):
        #every book have only one structure
        last_para = self.conn.get("select num,title,source_url from %s order by id desc limit 1" % (self._table_name,))
        if last_para:
            return False,last_para['source_url']
        return True,None

    def gen_insert_queue(self):
        self.qu = Queue()
        for p in self.para:
            tmp = self.gen_one_para_dic(p)
            if tmp:
                if self.at:
                    try:
                        self.qu.put(tmp)
                    except:
                        pass
                else:
                    if tmp['source_url'] == self.last_url:
                        self.at = True

        
    def process(self,conn):
        self.conn = conn
        self.ensure_table_exist()
        self.ensure_news_table_exist()
        self.at,self.last_url = self.gen_last()
        
        self.para = self.menu_parser()
        self.gen_insert_queue()
        
        while True:
        
            if self.qu.empty():
                print 'over'
                break
            tmp = self.qu.get()
            url = tmp['source_url']
            try:
                num = self.gen_url_num(url)
                file_name = '%s_%s.txt' % (self._name,num,)
                if os.path.exists(file_name):
                    continue
                while True:
                    try:
                        con_str = self.para_parser(url)
                        if con_str:
                            break
                    except:
                        print url
                fp = file(file_name,'w')
                fp.write(con_str)
                fp.close()
                self.conn.execute("insert into %s (num,title,source_url) values('%s','%s','%s')" % (self._table_name,num.encode('utf-8'),tmp['title'].encode('utf-8'),tmp['source_url'].encode('utf-8'),))
                self.conn.execute("insert into %s (belong,title,num) values('%s','%s','%s')" % (conf.NEWS_TABLE_NAME,self._name,tmp['title'].encode('utf-8'),num.encode('utf-8'),))
            except Exception,e:
                print url

    def translate_link(self,num):
        return '/%s/detail/%s' % (self._name,num,)

    @property
    def dir_name(self):
        return self._dir_name

    @property
    def main_page(self):
        return self._main_page
        
    @property
    def table_name(self):
        return self._table_name

    @property
    def name(self):
        return self._name

