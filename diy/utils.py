# -*- coding: utf-8 -*-
import re
import os,os.path
def filter_link(content):
    content = re.sub(r'<a[^>]*>','',content)
    content = re.sub(r'</a>','',content)
    return content

def gen_wdqk_path():
    return os.path.join(os.environ['OPENSHIFT_REPO_DIR'],'..','wudongqiankun')
