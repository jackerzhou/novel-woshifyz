# -*- coding:utf-8 -*-

import tornado.database
from bs4 import BeautifulSoup
import urllib
import re
from Queue import Queue
import re
import os,os.path

def get_content(qu):
    while True:
        if qu.empty():
            print 'over'
            break
        url = qu.get()
        try:
            num = re.match(r'http://www.saesky.net/wudongqiankun/(\S+?)\.html',url).group(1)
            file_name = 'wdqk_%s.txt' % (num,)
            if os.path.exists(file_name):
                continue
            content = urllib.urlopen(url).read()
            c_soup = BeautifulSoup(content)
            content_body = c_soup.find('div',{'class':'content-body'})
            script_garbage = content_body.findAll('script')
            [t.extract() for t in script_garbage]
            div_garbage = content_body.findAll('div',{'style':re.compile('.+')})
            [t.extract() for t in div_garbage]
            con_str = str(content_body)
            fp = file(file_name,'w')
            fp.write(con_str)
            fp.close()
        except Exception,e:
            print url
            
def main():
    main_content = urllib.urlopen("http://www.saesky.net/wudongqiankun/").read()
    con_soup = BeautifulSoup(main_content)
    mulu = con_soup.find('div',{'class':'box'})
    para = mulu.findAll('li')
    res = []
    conn = tornado.database.Connection('127.6.123.1','novel',user='admin',password='b4E3e3T8KRj8')

    last_num = conn.get("select num,name from wdqk order by id desc limit 1")['num']

    at = False
    qu = Queue()


    for p in para:
        if at:
            try:
                tmp = {}
                tmp['href'] = p.a['href']
                tmp['name'] = p.string
                conn.execute("insert into wdqk (num,name) values(%s,%s)",tmp['href'].encode('utf-8'),tmp['name'].encode('utf-8'))
                qu.put(tmp['href'])
            except:
                pass
        else:
            if p.a['href'] == last_num:
                at = True

    path = os.path.join(os.path.dirname(__file__),'wudongqiankun')
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    get_content(qu)

if __name__ == '__main__':
    main()
