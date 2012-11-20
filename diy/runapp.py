import os,os.path
import tornado.web
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.database
import re
from utils import filter_link

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
        filename = os.path.join(os.path.dirname(__file__),"./wudongqiankun/%s" % (filename,))
        try:
            fp = open(filename,'r')
            content = fp.read()
            num = 'http://www.saesky.net/wudongqiankun/%s.html' % (id,)
            cur = self.w_conn.get("select id,name from wdqk where num='%s' " % (num,))
            together = self.w_conn.query("select id,num,name from wdqk where id>=%d and id<=%d" % (int(cur['id'])-4,int(cur['id'])+5,))
            for para in together:
                url = para['num']
                num = re.match(r'http://www.saesky.net/wudongqiankun/(\S+?)\.html',url).group(1)
                file_name = 'wdqk_%s.txt' % (num,)
                para['num'] = '/detail/%s' % (num,)
            self.render('detail.html',dic={'content':filter_link(content),'cur':cur,'together':together})
        except Exception,e:
            pass

    def __del__(self):
        self.w_conn.close()

if __name__ == '__main__':
    app = tornado.web.Application([('/wdqk',MainHandler),('/detail/(\S+)$',DetailHandler)],
            template_path=os.path.join(os.path.dirname(__file__), "./template"),static_path=os.path.join(os.path.dirname(__file__), "./static"),debug=True,autoescape=None
            )
    address = os.environ['OPENSHIFT_INTERNAL_IP']
    app.listen(8888,address=address)
    tornado.ioloop.IOLoop.instance().start()
