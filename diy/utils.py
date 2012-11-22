# -*- coding: utf-8 -*-
import re
def filter_link(content):
    content = re.sub(r'<a[^>]*>','',content)
    content = re.sub(r'</a>','',content)
    return content
