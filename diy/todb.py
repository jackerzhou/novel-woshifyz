# -*- coding: utf-8 -*-
import tornado.database
from bs4 import BeautifulSoup
import urllib
import re
main_content = urllib.urlopen("http://www.saesky.net/wudongqiankun/").read()
con_soup = BeautifulSoup(main_content)
mulu = con_soup.find('div',{'class':'box'})
para = mulu.findAll('li')
res = []
conn = tornado.database.Connection('127.6.123.1','novel',user='admin',password='b4E3e3T8KRj8')
for p in para:
    try:
        tmp = {}
        tmp['href'] = p.a['href']
        tmp['name'] = p.string
        conn.execute("insert into wdqk (num,name) values(%s,%s)",tmp['href'].encode('utf-8'),tmp['name'].encode('utf-8'))
    except:
        pass
