# -*- coding: utf-8 -*-
import re, json

def load_objects(path):
    html = open(path, encoding='utf-8').read()
    ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))
    ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))
    return ds, ep, html

old_ds, old_ep, old_html = load_objects('index.html.bak-specwktme')
new_ds, new_ep, new_html = load_objects('index.html')

# Keys in old but missing in new (should be none)
lost_ds = set(old_ds) - set(new_ds)
lost_ep = set(old_ep) - set(new_ep)
print('DETAILED_SPECS keys lost:', len(lost_ds), list(lost_ds)[:10])
print('ENHANCED keys lost:', len(lost_ep), list(lost_ep)[:10])

# Changed values for existing keys (should be none)
changed_ds = [k for k in old_ds if k in new_ds and old_ds[k] != new_ds[k]]
changed_ep = [k for k in old_ep if k in new_ep and old_ep[k] != new_ep[k]]
print('DETAILED_SPECS changed values:', len(changed_ds), changed_ds[:10])
print('ENHANCED changed values:', len(changed_ep), changed_ep[:10])

# New keys (should be exactly the 8 WKT/ME)
new_ds_keys = set(new_ds) - set(old_ds)
new_ep_keys = set(new_ep) - set(old_ep)
print('DETAILED_SPECS new keys:', sorted(new_ds_keys))
print('ENHANCED new keys:', sorted(new_ep_keys))

# Overall HTML changed? only the two insertion regions should differ.
# Quickly confirm the file starts and ends identically (structure intact).
print('old html starts same:', old_html[:2000] == new_html[:2000])
print('old html ends same:', old_html[-2000:] == new_html[-2000:])
print('new html size:', len(new_html.encode('utf-8')), 'old:', len(old_html.encode('utf-8')))
