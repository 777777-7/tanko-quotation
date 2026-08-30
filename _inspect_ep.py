# -*- coding: utf-8 -*-
import re, json
html = open('index.html', encoding='utf-8').read()

m = re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S)
print('ENHANCED regex found:', bool(m))
if m:
    ep = json.loads(m.group(1))
    keys = list(ep.keys())
    print('total keys:', len(keys))
    print('first 3:', keys[:3])
    print('last 3:', keys[-3:])
    # raw start
    print('=== ENHANCED raw start ===')
    print(html[m.start(1):m.start(1)+600])
    # last key raw
    lk = keys[-1]
    idx = html.find('"' + lk + '"', m.start(1))
    print('=== ENHANCED raw tail ===')
    print(html[idx:idx+300])
