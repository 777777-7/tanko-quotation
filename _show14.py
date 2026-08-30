# -*- coding: utf-8 -*-
import re, json
html = open('index.html', encoding='utf-8').read()
ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))

# Find rack-like / workbench-like entries
for k in ds:
    v = ds[k]
    if isinstance(v, dict) and (v.get('material') or '').lower() in ('steel', 'laminate', 'wood') or 'rack' in k.lower() or 'workbench' in k.lower():
        if k.upper().startswith(('RA', 'RB', 'RC', 'TA', 'TE', 'A4', 'WB', 'WKT', 'ME', 'KQ', 'KP')):
            print('----', k, '----')
            print(json.dumps(v, ensure_ascii=False))
