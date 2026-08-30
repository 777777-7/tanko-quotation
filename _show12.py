# -*- coding: utf-8 -*-
import re
html = open('index.html', encoding='utf-8').read()

def extract_func(src, name):
    start = src.find('function ' + name)
    if start < 0:
        return None
    # find opening brace
    ob = src.find('{', start)
    depth = 0
    i = ob
    while i < len(src):
        c = src[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return src[start:i+1]
        i += 1
    return src[start:]

for fn in ['buildItemRowHtml']:
    body = extract_func(html, fn)
    print('='*30, fn, 'len', len(body), '='*30)
    print(body)
