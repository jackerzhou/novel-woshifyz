# -*- coding: utf-8 -*-
import sys
import os,os.path
import tornado.web
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.database
import re
from utils import filter_link,gen_content_path,book_relative_import
from conf import books,gen_dbconf

class Application(tornado.web.Application):
    def __init__(self,mode):
        handlers = [
            ('/',IndexHandler),
            ('/(\w+)$',MainHandler),
            ('/([^/]+?)/detail/(\S+)$',DetailHandler)
        ] 
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "./template"),
            static_path=os.path.join(os.path.dirname(__file__), "./static"),
            debug=True,
            autoescape=None
        )
        super(Application,self).__init__(handlers,**settings)
        self.mode = mode
        
        dbconf = gen_dbconf(self.mode)
        self.conn = tornado.database.Connection(dbconf['host'],dbconf['db'],user=dbconf['user'],password=dbconf['passwd'])
        self.books = {}
        self.book_names = {}
        for key in books:
            book_module = book_relative_import(books[key])
            book = book_module()
            self.books[key] = book
            self.book_names[key] = books[key][2]

    def __del__(self):
        self.conn.close()

class MainHandler(tornado.web.RequestHandler):
    @property
    def conn(self):
        return self.application.conn

    def get(self,id):
        book = self.application.books[str(id).strip()]
        all_para = self.conn.query("select num,title from %s" % (book.table_name,))
        for para in all_para:
            para['num'] = book.translate_link(para['num'])
        self.render('main.html',dic={'all':all_para,'title':self.application.book_names[str(id).strip()]})

class DetailHandler(tornado.web.RequestHandler):
    @property
    def conn(self):
        return self.application.conn

    def get(self,name,id):
        book = self.application.books[name]
        filename = '%s_%s.txt' % (name,id,)
        filename = os.path.join(gen_content_path(self.application.mode,book.dir_name),filename)
        try:
            fp = open(filename,'r')
            content = fp.read()
            cur = self.conn.get("select id,num,title from %s where num='%s' " % (name,id,))
            together_next = self.conn.query("select id,num,title from %s where id>=%d order by id limit 6" % (name,int(cur['id']),))
            together = self.conn.query("select id,num,title from %s where id<%d order by id desc limit 3" % (name,int(cur['id']),))
            together.reverse()
            together.extend(together_next)
            cur_num = 0
            for i,para in enumerate(together):
                if para['id'] == cur['id']:
                    cur_num = i
                para['num'] = book.translate_link(para['num'])
            pre_para = '0'
            next_para = '0'
            if cur_num-1>=0:
                pre_para = together[cur_num-1]['num']
            if cur_num+1<len(together):
                next_para = together[cur_num+1]['num']
            self.render('detail.html',dic={'content':filter_link(content),'cur':cur,'together':together,'pre':pre_para,'next':next_para})
        except Exception,e:
            pass

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        res = []
        for key,book in books.items():
            tmp = {}
            tmp['title'] = book[2]
            tmp['url'] = '/%s' % (key,)
            res.append(tmp)
        self.render('index.html',dic=res)

if __name__ == '__main__':
    try:
        mode = sys.argv[1]
    except:
        mode = 'pro'
    app = Application(mode)
    if mode == 'dev' or mode == 'office':
        address = 'localhost'
    else:
        address = os.environ['OPENSHIFT_INTERNAL_IP']
    app.listen(8080,address=address)
    tornado.ioloop.IOLoop.instance().start()
