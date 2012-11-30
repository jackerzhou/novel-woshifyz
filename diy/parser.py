from bs4 import BeautifulSoup
import urllib
import re

def wdqk_para_parser(url):
    
    content = urllib.urlopen(url).read()
    c_soup = BeautifulSoup(content)
    content_body = c_soup.find('div',{'class':'content-body'})
    script_garbage = content_body.findAll('script')
    [t.extract() for t in script_garbage]
    div_garbage = content_body.findAll('div',{'style':re.compile('.+')})
    [t.extract() for t in div_garbage]
    return str(content_body)

def wdqk_menu_parser(url):

    main_content = urllib.urlopen(url).read()
    con_soup = BeautifulSoup(main_content)
    mulu = con_soup.find('div',{'class':book['para_class']})
    para = mulu.findAll('li')
    return para
