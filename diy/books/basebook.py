from Queue import Queue
import os,os.path
from bs4 import BeautifulSoup
import urllib

class BaseBook(object):

    def menu_parser(self):
        raise NotImplementedError    

    def para_parser(self):
        raise NotImplementedError

    def gen_one_para_dic(self,para):
        ''' 
            {'source_url':xxx,'title':xxx}
        '''
        raise NotImplementedError

    def gen_url_num(self,url):
        raise NotImplementedError

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
        self.at,self.last_url = self.gen_last()
        
        main_content = urllib.urlopen(self._main_page).read()
        con_soup = BeautifulSoup(main_content)
        self.para = self.menu_parser(con_soup)
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
                self.conn.execute("insert into %s (num,title,source_url) values('%s','%s','%s')" % (self._table_name,num.encode('utf-8'),tmp['title'].encode('utf-8'),tmp['source_url'].encode('utf-8'),))
                if os.path.exists(file_name):
                    continue
                while True:
                    try:
                        content = urllib.urlopen(url).read()
                        c_soup = BeautifulSoup(content)
                        con_str = self.para_parser(c_soup)
                        if con_str:
                            break
                    except:
                        print url
                fp = file(file_name,'w')
                fp.write(con_str)
                fp.close()
                #self.conn.execute("insert into %s (num,title,source_url) values('%s','%s','%s')" % (self._table_name,num,tmp['title'].encode('utf-8'),tmp['source_url'].encode('utf-8'),))
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

