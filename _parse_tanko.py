# -*- coding: utf-8 -*-
import re, html as htmlmod

for name in ['wkt', 'me']:
    raw = open('_tanko_' + name + '.html', encoding='utf-8').read()
    print('='*20, name.upper(), '='*20)
    # strip scripts/styles
    raw = re.sub(r'<script.*?</script>', ' ', raw, flags=re.S)
    raw = re.sub(r'<style.*?</style>', ' ', raw, flags=re.S)
    # Extract text around spec keywords
    text = re.sub(r'<[^>]+>', '\n', raw)
    text = htmlmod.unescape(text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    # find relevant lines
    for i, l in enumerate(lines):
        if re.search(r'Model No|Dimensions|Material|Loading|Shelf|Workbench-top|load capacity|WKT-5102|ME-32|WPK-21', l):
            print(l[:160])
