# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
print('file size bytes:', len(html.encode('utf-8')))

ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))

print('DETAILED_SPECS total keys:', len(ds))
print('ENHANCED_PRODUCTS total keys:', len(ep))

wkt_ds = {k: ds[k] for k in ds if k.upper().startswith('WKT')}
me_ds = {k: ds[k] for k in ds if k.upper().startswith('ME')}
wkt_ep = {k: ep[k] for k in ep if k.upper().startswith('WKT')}
me_ep = {k: ep[k] for k in ep if k.upper().startswith('ME')}
print('WKT in DETAILED_SPECS:', len(wkt_ds), '->', sorted(wkt_ds))
print('ME in DETAILED_SPECS:', len(me_ds), '->', sorted(me_ds))
print('WKT in ENHANCED:', len(wkt_ep), '->', sorted(wkt_ep))
print('ME in ENHANCED:', len(me_ep), '->', sorted(me_ep))

# Show the inserted entries
print()
print('=== new DETAILED_SPECS entries ===')
for k in sorted(list(wkt_ds) + list(me_ds)):
    print(k, '=>', json.dumps(ds[k], ensure_ascii=False))
print()
print('=== new ENHANCED entries ===')
for k in sorted(list(wkt_ep) + list(me_ep)):
    print(k, '=>', repr(ep[k]))
