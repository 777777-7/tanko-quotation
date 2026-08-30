# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))

ds_file = json.load(open('data/detailed_specs.json', encoding='utf-8'))
file_keys = set(ds_file.keys())
inline_keys = set(ds.keys())
missing = sorted(k for k in file_keys if k not in inline_keys)
print('missing from inline DETAILED_SPECS:', len(missing))
wkt_miss = [k for k in missing if k.upper().startswith('WKT')]
me_miss = [k for k in missing if k.upper().startswith('ME')]
print('  WKT missing:', wkt_miss)
print('  ME missing:', me_miss)

# Now: all PRODUCT_DATA skus -> which have DETAILED_SPECS and/or ENHANCED_PRODUCTS
skus = re.findall(r'sku:\s*"([^"]+)"', html)
uniq = sorted(set(skus))
print()
print('PRODUCT_DATA unique skus:', len(uniq))
no_ds = [s for s in uniq if s not in ds]
no_ep = [s for s in uniq if s not in ep]
no_both = [s for s in uniq if s not in ds and s not in ep]
print('skus missing DETAILED_SPECS:', len(no_ds))
print('skus missing ENHANCED_PRODUCTS:', len(no_ep))
print('skus missing BOTH (would show "Specifications available on request"):', len(no_both))
print('  ->', no_both)
print()
print('skus with DETAILED_SPECS but no ENHANCED:', len([s for s in uniq if s in ds and s not in ep]))
print('skus with ENHANCED but no DETAILED:', len([s for s in uniq if s in ep and s not in ds]))
