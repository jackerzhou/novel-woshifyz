# -*- coding:utf-8 -*-

import tornado.database
from bs4 import BeautifulSoup
import urllib
import re
from Queue import Queue
import re
import os,os.path
from utils import gen_wdqk_path

def get_content(conn,qu):
    while True:
        if qu.empty():
            print 'over'
            break
        tmp = qu.get()
        url = tmp['href']
        try:
            num = re.match(r'http://www.saesky.net/wudongqiankun/(\S+?)\.html',url).group(1)
            file_name = 'wdqk_%s.txt' % (num,)
            if os.path.exists(file_name):
                continue
            while True:
                try:
                    content = urllib.urlopen(url).read()
                    c_soup = BeautifulSoup(content)
                    content_body = c_soup.find('div',{'class':'content-body'})
                    script_garbage = content_body.findAll('script')
                    [t.extract() for t in script_garbage]
                    div_garbage = content_body.findAll('div',{'style':re.compile('.+')})
                    [t.extract() for t in div_garbage]
                    con_str = str(content_body)
                    if con_str:
                        break
                except:
                    print url
            fp = file(file_name,'w')
            fp.write(con_str)
            fp.close()
            conn.execute("insert into wdqk (num,name) values(%s,%s)",tmp['href'].encode('utf-8'),tmp['name'].encode('utf-8'))
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
                qu.put(tmp)
            except:
                pass
        else:
            if p.a['href'] == last_num:
                at = True

    path = gen_wdqk_path()
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    get_content(conn,qu)
    conn.close()

if __name__ == '__main__':
    main()
