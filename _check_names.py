# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))

# PRODUCT_DATA is a JS array - extract sku/name pairs via regex
m = re.search(r'const PRODUCT_DATA = \[(.*?)\];', html, re.S)
block = m.group(1)
# Each entry looks like: {sku: "XXX", name: "YYY", base_price: 123, ...}
entries = re.findall(r'\{\s*sku:\s*"([^"]*)",\s*name:\s*"((?:[^"\\]|\\.)*)"', block)
print('PRODUCT_DATA entries found:', len(entries))

no_ep = [(sku, name) for sku, name in entries if sku not in ep]
print('without ENHANCED:', len(no_ep))
print()
for sku, name in no_ep[:20]:
    # unescape \n
    name_display = name.replace('\\n', ' | ')
    print(sku, '=>', name_display[:150])
