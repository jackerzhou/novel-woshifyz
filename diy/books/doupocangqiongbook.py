from basebook import BaseBook
import re
from bs4 import BeautifulSoup
import urllib

class DoupocangqiongBook(BaseBook):
    def __init__(self):
        self._name='doupocangqiong'
        self._dir_name = 'doupocangqiong'
        self._main_page= 'http://www.59to.com/files/article/xiaoshuo/3/3215/'
        self._table_name = 'doupocangqiong'
        #self._from_encoding = 'GB18030'
        self._from_encoding = None

    def gen_url_num(self,url):
        return re.match(r'(\S+?)\.html',url).group(1)

    def menu_parser(self):
        main_content = urllib.urlopen(self._main_page).read()
        if self._from_encoding:
            con_soup = BeautifulSoup(main_content,from_encoding=self._from_encoding)
        else:
            con_soup = BeautifulSoup(main_content)
        mulu = con_soup.find('table',{'class':'acss'})
        para = mulu.findAll('td',{'class':'www'})
        return para
    
    def para_parser(self,url):
        content = urllib.urlopen(self.make_para_url(url)).read()
        if self._from_encoding:
            c_soup = BeautifulSoup(content,from_encoding=self._from_encoding)
        else:
            c_soup = BeautifulSoup(content)
        content_body = c_soup.find('div',{'id':'content'})
        script_garbage = content_body.findAll('script')
        [t.extract() for t in script_garbage]
        div_garbage = content_body.findAll('div',{'style':re.compile('.+')})
        [t.extract() for t in div_garbage]
        return str(content_body)

    def gen_one_para_dic(self,para):
        try:
            tmp = {}
            tmp['source_url'] = para.a['href']
            tmp['title'] = para.string
            return tmp
        except:
            return None

        
    def make_para_url(self,url):
        return '%s%s' % (self._main_page,url,)
    
