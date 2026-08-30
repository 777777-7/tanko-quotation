# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))

pd_match = re.search(r'const PRODUCT_DATA = \[(.*?)\];', html, re.S)
pd_entries = re.findall(r'\{\s*sku:\s*"([^"]*)",\s*name:\s*"((?:[^"\\]|\\.)*)"', pd_match.group(1))
all_skus = [s for s, _ in pd_entries if s != '<SKU code>']

print('Total real PRODUCT_DATA SKUs:', len(all_skus))
print('DETAILED_SPECS total:', len(ds))
print('ENHANCED_PRODUCTS total:', len(ep))

missing_ds = [s for s in all_skus if s not in ds]
missing_ep = [s for s in all_skus if s not in ep]
missing_both = [s for s in all_skus if s not in ds and s not in ep]
print()
print('Missing DETAILED_SPECS:', len(missing_ds), missing_ds[:10])
print('Missing ENHANCED:', len(missing_ep), missing_ep[:10])
print('Missing both:', len(missing_both))

# Verify a few newly added entries
print()
print('=== Sample newly added DETAILED_SPECS ===')
for s in ['DA-31 (BLACK)', 'KQ-105', 'WB-7051M', 'WE-10031-111MN']:
    if s in ds:
        print(s, '=>', json.dumps(ds[s], ensure_ascii=False)[:200])
    else:
        print(s, '=> NOT FOUND')

print()
print('=== Sample newly added ENHANCED ===')
for s in ['DA-31 (BLACK)', 'KQ-105', 'WB-7051M']:
    if s in ep:
        print(s, '=>', repr(ep[s][:120]))
    else:
        print(s, '=> NOT FOUND')

# Verify layout changes
print()
print('=== Layout checks ===')
print('Forced page-break-after div removed:', 'page-break-after: always;' not in html)
print('Product Photos heading has margin-top:', 'margin:14pt 0 8pt 0' in html)
print('Product Photos heading has page-break-after:avoid:', 'page-break-after:avoid' in html)
print('Photo cell has page-break-inside:avoid:', 'page-break-inside:avoid;' in html)
print('Photo row has page-break-inside:avoid (existing):', 'page-break-inside:avoid;' in html)

# Verify no syntax issues: the objects parse as valid JSON (already done above)
print()
print('Both inline objects parse as valid JSON: OK')
print('File size:', len(html.encode('utf-8')), 'bytes')
