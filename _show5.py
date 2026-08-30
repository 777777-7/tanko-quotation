# -*- coding: utf-8 -*-
import json, os

base = r'C:\Users\User\Documents\GitHub\tanko-website-1-'
pc = json.load(open(os.path.join(base, 'product_content.json'), encoding='utf-8'))
for slug in ['wkt_5102', 'me']:
    if slug in pc:
        print('===== product_content.json[' + slug + '] =====')
        print(json.dumps(pc[slug], ensure_ascii=False, indent=1))
