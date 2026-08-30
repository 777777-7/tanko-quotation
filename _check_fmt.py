# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))
skus = sorted(set(re.findall(r'sku:\s*"([^"]+)"', html)))
data_specs = json.load(open('data/detailed_specs.json', encoding='utf-8'))

# SKUs to back-fill
to_fill = [s for s in skus if s not in ds and s != '<SKU code>']
print('To back-fill DETAILED_SPECS:', len(to_fill))

# Check field consistency
field_sets = {}
for s in to_fill:
    if s in data_specs:
        keys = tuple(sorted(data_specs[s].keys()))
        field_sets.setdefault(keys, []).append(s)

print('Distinct field sets in data JSON:')
for keys, members in field_sets.items():
    print('  ', keys, '->', len(members), 'e.g.', members[:3])

# Show a few sample entries
print()
for s in to_fill[:5]:
    if s in data_specs:
        print(s, '=>', json.dumps(data_specs[s], ensure_ascii=False))

# Check for entries with null/empty fields
print()
null_count = 0
for s in to_fill:
    if s in data_specs:
        d = data_specs[s]
        if not d.get('dimension') and not d.get('material'):
            null_count += 1
print('Entries with no dimension AND no material:', null_count)
