# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
out = {}
out['wkt_count'] = len(re.findall(r'WKT', html))
wkt_pos = [m.start() for m in re.finditer(r'WKT', html)]
out['wkt_ctx'] = []
for p in wkt_pos:
    s = max(0, p-60); e = min(len(html), p+80)
    out['wkt_ctx'].append({'pos': p, 'ctx': html[s:e].replace('\n', ' ')})
out['me_count'] = len(re.findall(r'ME-', html))
me_pos = [m.start() for m in re.finditer(r'ME-', html)]
out['me_ctx'] = []
for p in me_pos[:30]:
    s = max(0, p-60); e = min(len(html), p+80)
    out['me_ctx'].append({'pos': p, 'ctx': html[s:e].replace('\n', ' ')})
with open('_dbg_wkt.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('written', len(out['wkt_ctx']), len(out['me_ctx']))
