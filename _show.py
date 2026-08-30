# -*- coding: utf-8 -*-
import json
d = json.load(open('_dbg_wkt.json', encoding='utf-8'))
print('WKT positions:', [i['pos'] for i in d['wkt_ctx']])
print('ME positions:', [i['pos'] for i in d['me_ctx']])
# Region boundaries
import re
html = open('index.html', encoding='utf-8').read()
for kw in ['const PRODUCT_DATA', 'const ENHANCED_PRODUCTS', 'const DETAILED_SPECS']:
    print(kw, html.find(kw))
