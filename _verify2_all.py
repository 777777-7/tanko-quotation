# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))

# 1. Check the specific page break div
div_pattern = '<div style="page-break-after: always;"></div>'
print('Forced page-break DIV present:', div_pattern in html)
print('CSS .page-break class present:', '.page-break { page-break-after: always; }' in html)
print('Replacement comment present:', 'Product photos flow naturally' in html)

# 2. Find actual KQ, WB, WE SKUs
pd_match = re.search(r'const PRODUCT_DATA = \[(.*?)\];', html, re.S)
pd_entries = re.findall(r'\{\s*sku:\s*"([^"]*)"', pd_match.group(1))
for prefix in ['KQ', 'WB', 'WE']:
    skus = [s for s in pd_entries if s.startswith(prefix)]
    print()
    print(prefix, 'series (' + str(len(skus)) + '):', skus[:8])
    # check first 3 have specs
    for s in skus[:3]:
        print('  ', s, 'DS=', s in ds, 'EP=', s in ep)

# 3. Verify a combo SKU with + in name
combos = [s for s in pd_entries if '+' in s]
print()
print('Combo SKUs sample:', combos[:5])
for s in combos[:3]:
    print('  ', s, 'DS=', s in ds, 'EP=', s in ep)
    if s in ep:
        print('    EP:', repr(ep[s][:100]))
