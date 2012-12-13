# -*- coding:utf-8 -*-

import tornado.database
import re
import os,os.path
from utils import gen_content_path,book_relative_import
from conf import books,gen_dbconf
from dbpool import DBPool
            
def main(mode,novel):
    dbconf = gen_dbconf(mode)
    #conn = tornado.database.Connection(dbconf['host'],dbconf['db'],user=dbconf['user'],password=dbconf['passwd'])
    pool = DBPool(host=dbconf['host'],database=dbconf['db'],user=dbconf['user'],password=dbconf['passwd'],min_conn=2,max_conn=3)
    conn = pool.connect()
    if not novel:
        for key in books:
            if mode == 'pro' and books[key][3] == True:
                pass
            else:
                book_module = book_relative_import(books[key])
                book = book_module()
                path = gen_content_path(mode,book.dir_name)
                if not os.path.exists(path):
                    os.mkdir(path)
                os.chdir(path)

                book.process(conn)
    else:
        key = novel
        if mode == 'pro' and books[key][3] == True:
            pass
        else:
            book_module = book_relative_import(books[key])
            book = book_module()
            path = gen_content_path(mode,book.dir_name)
            if not os.path.exists(path):
                os.mkdir(path)
            os.chdir(path)

            book.process(conn)

    conn.close()
    pool.close()

if __name__ == '__main__':
    import sys
    try:
        mode = sys.argv[1]
        novel = sys.argv[2]
    except:
        mode='pro'
        novel = None
    main(mode,novel)
