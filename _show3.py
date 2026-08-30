# -*- coding: utf-8 -*-
import json, os

base = r'C:\Users\User\Documents\GitHub\tanko-website-1-'

def load(name):
    p = os.path.join(base, name)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding='utf-8'))
        except Exception as e:
            return {'__err__': str(e)}
    return None

for fn in ['products.json', 'product_content.json', 'product_content_v2.json', 'tanko_variants.json', 'tanko_catalog_extracted.json']:
    d = load(fn)
    print('=====', fn, '=====')
    if d is None:
        print('  MISSING')
        continue
    if isinstance(d, dict):
        if '__err__' in d:
            print('  parse err:', d['__err__'])
            continue
        keys = list(d.keys())
        print('  type dict, keys:', len(keys))
        wkt = [k for k in keys if str(k).upper().startswith('WKT')]
        me = [k for k in keys if str(k).upper().startswith('ME')]
        print('  WKT:', wkt[:10])
        print('  ME:', me[:10])
        # sample structure
        if keys:
            k0 = keys[0]
            v0 = d[k0]
            print('  sample key type:', type(v0).__name__)
            if isinstance(v0, dict):
                print('  sample subkeys:', list(v0.keys())[:15])
    elif isinstance(d, list):
        print('  type list, len:', len(d))
        if d:
            print('  sample[0] type:', type(d[0]).__name__)
            if isinstance(d[0], dict):
                print('  sample[0] keys:', list(d[0].keys())[:20])
                # search for WKT/ME
                wkt = [x for x in d if isinstance(x, dict) and str(x.get('sku', x.get('model_no', ''))).upper().startswith('WKT')]
                me = [x for x in d if isinstance(x, dict) and str(x.get('sku', x.get('model_no', ''))).upper().startswith('ME')]
                print('  WKT entries:', len(wkt), '| ME entries:', len(me))
