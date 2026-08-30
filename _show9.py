# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))

# Show sample ENHANCED_PRODUCTS entries for workbench/rack-like products
targets = ['EA-7041', 'WB-57F', 'TA-115', 'RY-01SA', 'A4A-106', 'KL-1303', 'KP-4701']
for t in targets:
    if t in ep:
        print('---- ENHANCED', t, '----')
        print(repr(ep[t]))
    else:
        print('---- ENHANCED', t, 'MISSING ----')

# Show PRODUCT_DATA names for WKT/ME
print()
print('### PRODUCT_DATA names for WKT/ME ###')
for m in re.finditer(r'\{ sku: "([^"]+)", name: "((?:[^"\\]|\\.)*)", base_price: ([\d.]+) \}', html):
    sku, name, bp = m.group(1), m.group(2), m.group(3)
    if sku.upper().startswith('WKT') or sku.upper().startswith('ME'):
        print('----', sku, '----')
        print(repr(name.replace('\\n', '\n')))
