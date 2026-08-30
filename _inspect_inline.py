# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()

# DETAILED_SPECS (correct regex)
m = re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S)
ds = json.loads(m.group(1))
wkt_ds = [k for k in ds if k.upper().startswith('WKT')]
me_ds = [k for k in ds if k.upper().startswith('ME')]
print('DETAILED_SPECS total keys:', len(ds))
print('  WKT:', wkt_ds)
print('  ME:', me_ds)

# ENHANCED_PRODUCTS
m = re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S)
ep = json.loads(m.group(1))
wkt_ep = [k for k in ep if k.upper().startswith('WKT')]
me_ep = [k for k in ep if k.upper().startswith('ME')]
print('ENHANCED_PRODUCTS total keys:', len(ep))
print('  WKT:', wkt_ep)
print('  ME:', me_ep)

# PRODUCT_DATA skus
skus = re.findall(r'sku:\s*"([^"]+)"', html)
wkt = sorted(set(s for s in skus if s.upper().startswith('WKT')))
me = sorted(set(s for s in skus if s.upper().startswith('ME')))
print('PRODUCT_DATA skus total:', len(skus))
print('  WKT:', wkt)
print('  ME:', me)

# Compare: which data-file keys are missing from inline DETAILED_SPECS?
ds_file = json.load(open('data/detailed_specs.json', encoding='utf-8'))
file_keys = set(ds_file.keys())
inline_keys = set(ds.keys())
missing = sorted(k for k in file_keys if k not in inline_keys)
print('=== detailed_specs.json keys missing from inline DETAILED_SPECS:', len(missing))
print(missing[:200])
