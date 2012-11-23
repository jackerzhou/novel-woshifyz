# -*- coding: utf-8 -*-
import os,os.path
import tornado.web
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.database
import re
from utils import filter_link,gen_wdqk_path

class MainHandler(tornado.web.RequestHandler):
    w_conn = tornado.database.Connection('127.6.123.1','novel',user='admin',password='b4E3e3T8KRj8')
    def get(self):
        all_para = self.w_conn.query("select num,name from wdqk")
        for para in all_para:
            url = para['num']
            num = re.match(r'http://www.saesky.net/wudongqiankun/(\S+?)\.html',url).group(1)
            file_name = 'wdqk_%s.txt' % (num,)
            para['num'] = '/detail/%s' % (num,)
        self.render('main.html',dic=all_para)

    def __del__(self):
        self.w_conn.close()

class DetailHandler(tornado.web.RequestHandler):
    w_conn = tornado.database.Connection('127.6.123.1','novel',user='admin',password='b4E3e3T8KRj8')
    def get(self,id):
        filename = 'wdqk_%s.txt' % (id,)
        filename = os.path.join(gen_wdqk_path(),filename)
        try:
            fp = open(filename,'r')
            content = fp.read()
            num = 'http://www.saesky.net/wudongqiankun/%s.html' % (id,)
            cur = self.w_conn.get("select id,name from wdqk where num='%s' " % (num,))
            together_next = self.w_conn.query("select id,num,name from wdqk where id>=%d order by id limit 6" % (int(cur['id']),))
            together = self.w_conn.query("select id,num,name from wdqk where id<%d order by id desc limit 3" % (int(cur['id']),))
            together.reverse()
            together.extend(together_next)
            cur_num = 0
            for i,para in enumerate(together):
                url = para['num']
                if para['id'] == cur['id']:
                    cur_num = i
                num = re.match(r'http://www.saesky.net/wudongqiankun/(\S+?)\.html',url).group(1)
                file_name = 'wdqk_%s.txt' % (num,)
                para['num'] = '/detail/%s' % (num,)
            pre_para = '0'
            next_para = '0'
            if cur_num-1>=0:
                pre_para = together[cur_num-1]['num']
            if cur_num+1<len(together):
                next_para = together[cur_num+1]['num']
            self.render('detail.html',dic={'content':filter_link(content),'cur':cur,'together':together,'pre':pre_para,'next':next_para})
        except Exception,e:
            pass

    def __del__(self):
        self.w_conn.close()


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/wdqk')

if __name__ == '__main__':
    app = tornado.web.Application([('/',IndexHandler),('/wdqk',MainHandler),('/detail/(\S+)$',DetailHandler)],
            template_path=os.path.join(os.path.dirname(__file__), "./template"),static_path=os.path.join(os.path.dirname(__file__), "./static"),debug=True,autoescape=None
            )
    address = os.environ['OPENSHIFT_INTERNAL_IP']
    app.listen(8080,address=address)
    tornado.ioloop.IOLoop.instance().start()
