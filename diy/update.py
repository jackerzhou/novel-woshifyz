# -*- coding:utf-8 -*-

import tornado.database
import re
from Queue import Queue
import os,os.path
from utils import gen_content_path
from conf import books,dbconf
import parser

def get_content(book,conn,qu):
    while True:
        if qu.empty():
            print 'over'
            break
        tmp = qu.get()
        url = tmp['href']
        try:
            num = re.match(book['url_re'],url).group(1)
            file_name = '%s_%s.txt' % (,book['id'],num,)
            if os.path.exists(file_name):
                continue
            while True:
                try:
                    para_parser = getattr(parser,'%s_para_parser' % (book['id'],))
                    con_str = para_parser(url)
                    if con_str:
                        break
                except:
                    print url
            fp = file(file_name,'w')
            fp.write(con_str)
            fp.close()
            conn.execute("insert into %s (num,name) values(%s,%s)" % (book['table'],tmp['href'].encode('utf-8'),tmp['name'].encode('utf-8'),))
        except Exception,e:
            print url
            
def main():
    conn = tornado.database.Connection(dbconf['host'],dbconf['db'],user=dbconf['user'],password=dbconf['passwd'])
    for key in books:
        book = books[key]
        menu_parser = getattr(parser,'%s_menu_parser' % (book['id'],))
        para = menu_parser(book['main_page'])
        res = []

        last_num = conn.get("select num,name from %s order by id desc limit 1" % (book['table'],))
        if last_num:
            at = False
            last_num = last_num['num']
        else:
            at = True
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

        path = gen_content_path(book['dir_name'])
        if not os.path.exists(path):
            os.mkdir(path)
        os.chdir(path)
        get_content(book,conn,qu)

    conn.close()

if __name__ == '__main__':
    main()
