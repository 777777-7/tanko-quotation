# -*- coding: utf-8 -*-
import json

ds = json.load(open('data/detailed_specs.json', encoding='utf-8'))
for pre in ['WKT', 'ME']:
    print('===== detailed_specs.json entries for', pre, '=====')
    for k in sorted(ds.keys()):
        if k.upper().startswith(pre):
            print(json.dumps({k: ds[k]}, ensure_ascii=False, indent=1))

# What about ENHANCED_PRODUCTS on disk?
enh = json.load(open('data/enhanced_products.json', encoding='utf-8'))
print('===== enhanced_products.json entries for WKT/ME =====')
for k in sorted(enh.keys()):
    if k.upper().startswith('WKT') or k.upper().startswith('ME'):
        print(k, '=>', repr(enh[k])[:300])
