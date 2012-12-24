# -*- coding: utf-8 -*-
import re
import os,os.path
def filter_link(content):
    content = re.sub(r'<a[^>]*>','',content)
    content = re.sub(r'</a>','',content)
    return content

def gen_content_path(mode,name):
    if mode == 'dev' or mode == 'office':
        return os.path.join(os.path.dirname(__file__),'../content',name)
    else:    
        return os.path.join(os.environ['OPENSHIFT_REPO_DIR'],'../content',name)

def book_relative_import(module_str):
    import_module = __import__(module_str[0],fromlist=[module_str[1]])
    return getattr(import_module,module_str[1])

def gen_data_path(mode):
    if mode == 'dev' or mode == 'office':
        return os.path.join(os.path.dirname(__file__),'../data')
    else:    
        return os.path.join(os.environ['OPENSHIFT_REPO_DIR'],'../data')
    
