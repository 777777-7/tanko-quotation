# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()

m = re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S)
print('matched:', bool(m))
if m:
    txt = m.group(1)
    print('matched text len:', len(txt))
    print('starts:', txt[:100])
    print('ends:', txt[-100:])
    try:
        ds = json.loads(txt)
        ks = list(ds.keys())
        print('parsed keys:', len(ks))
        print('first 5:', ks[:5])
        print('RY-01SA in ds:', 'RY-01SA' in ds)
    except Exception as ex:
        print('parse err:', ex)
