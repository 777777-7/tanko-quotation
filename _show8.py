# -*- coding: utf-8 -*-
import re
html = open('index.html', encoding='utf-8').read()

# Extract buildItemRowHtml function
for fn in ['buildItemRowHtml', 'buildPhotoCellHtml', 'buildPhotosGridHtml']:
    m = re.search(r'function ' + fn + r'\(.*?\n}', html, re.S)
    if m:
        print('='*20, fn, '='*20)
        print(m.group(0)[:3500])
        print()
