# -*- coding: utf-8 -*-
import json, os

base = r'C:\Users\User\Documents\GitHub\tanko-website-1-'

prod = json.load(open(os.path.join(base, 'products.json'), encoding='utf-8'))
print('=== website products.json WKT/ME entries (with specification) ===')
for p in prod:
    sku = str(p.get('sku', ''))
    if sku.upper().startswith('WKT') or sku.upper().startswith('ME'):
        print(json.dumps(p, ensure_ascii=False, indent=1))
