# -*- coding: utf-8 -*-
import re, html as htmlmod

for name, path in [('wkt', r'C:\Users\User\Documents\GitHub\tanko-website-1-\docs\workbench\wkt_5102\index.html'),
                   ('me', r'C:\Users\User\Documents\GitHub\tanko-website-1-\docs\rack\me\index.html')]:
    raw = open(path, encoding='utf-8').read()
    print('='*20, name.upper(), '='*20)
    # find spec tables: look for Model No / Dimensions rows
    # Extract all table rows containing Model No
    tables = re.findall(r'<table.*?</table>', raw, flags=re.S)
    for ti, t in enumerate(tables):
        if 'Model No' in t or 'Dimensions' in t or 'Loading' in t or 'WKT' in t or 'ME-3' in t:
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', t, flags=re.S)
            print('--- table', ti, '---')
            for r in rows:
                cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, flags=re.S)
                cells = [re.sub(r'<[^>]+>', ' ', c) for c in cells]
                cells = [htmlmod.unescape(re.sub(r'\s+', ' ', c)).strip() for c in cells]
                if any(cells):
                    print(' | '.join(cells))
