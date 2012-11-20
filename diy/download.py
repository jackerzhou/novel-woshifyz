# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import pdb
import urllib
from Queue import Queue
import os,os.path
import re


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
    queue = Queue()
    for p in para:
        try:
            queue.put(p.a['href'])
        except:
            pass

    path = os.path.join(os.path.dirname(__file__),'wudongqiankun')
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    from multiprocessing import Process
    for i in range(10):
        p = Process(target=get_content,args=(queue,))
        p.start()

if __name__ == '__main__':
    main()
