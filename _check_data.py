# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))
skus = sorted(set(re.findall(r'sku:\s*"([^"]+)"', html)))

# data/detailed_specs.json
data_specs = json.load(open('data/detailed_specs.json', encoding='utf-8'))
# The JSON might be a list or dict
print('data_specs type:', type(data_specs).__name__)
if isinstance(data_specs, list):
    print('data_specs count:', len(data_specs))
    print('first item keys:', list(data_specs[0].keys()) if data_specs else 'empty')
    # build a lookup by model_no
    data_by_model = {}
    for item in data_specs:
        mn = item.get('model_no', '')
        if mn:
            data_by_model[mn] = item
    print('data_by_model count:', len(data_by_model))
elif isinstance(data_specs, dict):
    print('data_specs keys sample:', list(data_specs.keys())[:5])
    data_by_model = data_specs

# SKUs without inline DETAILED_SPECS
no_ds = [s for s in skus if s not in ds]
no_ep = [s for s in skus if s not in ep]
no_both = [s for s in skus if s not in ds and s not in ep]

print()
print('Total SKUs:', len(skus))
print('Without inline DETAILED_SPECS:', len(no_ds))
print('Without inline ENHANCED:', len(no_ep))
print('Without either:', len(no_both))

# How many of no_ds have data in data_by_model?
have_data = [s for s in no_ds if s in data_by_model]
no_data = [s for s in no_ds if s not in data_by_model]
print()
print('Without inline DS but HAVE data in JSON:', len(have_data))
print('Without inline DS and NO data in JSON:', len(no_data))
print('Sample no_data:', no_data[:30])

# Check data_by_model keys that match PRODUCT_DATA skus
matched = [s for s in skus if s in data_by_model]
print()
print('PRODUCT_DATA SKUs found in data JSON:', len(matched))
print('data JSON total entries:', len(data_by_model))
