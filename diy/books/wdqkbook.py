from basebook import BaseBook
import re

class WdqkBook(BaseBook):
    def __init__(self):
        self._name='wdqk'
        self._dir_name = 'wudongqiankun'
        self._main_page= 'http://www.saesky.net/wudongqiankun/'
        self._table_name = 'wdqk'

    def gen_url_num(self,url):
        return re.match(r'http://www.saesky.net/wudongqiankun/(\S+?)\.html',url).group(1)

    def menu_parser(self,con_soup):
        mulu = con_soup.find('div',{'class':'box'})
        para = mulu.findAll('li')
        return para
    
    def para_parser(self,c_soup):
        content_body = c_soup.find('div',{'class':'content-body'})
        script_garbage = content_body.findAll('script')
        [t.extract() for t in script_garbage]
        div_garbage = content_body.findAll('div',{'style':re.compile('.+')})
        [t.extract() for t in div_garbage]
        return str(content_body)

    def gen_one_para_dic(self,para):
        tmp = {}
        tmp['source_url'] = para.a['href']
        tmp['title'] = para.string
        return tmp

        
    
