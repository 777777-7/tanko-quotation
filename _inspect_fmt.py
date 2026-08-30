# -*- coding: utf-8 -*-
import re, json
html = open('index.html', encoding='utf-8').read()

# Show exact inline format of a few DETAILED_SPECS entries
m = re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S)
start = m.start(1)
# print raw text from start to first ~1200 chars
print('=== DETAILED_SPECS raw start ===')
print(html[start:start+800])

# Find the END of DETAILED_SPECS object (before '};')
# Use the parsed object's last key to locate
ds = json.loads(m.group(1))
last_key = list(ds.keys())[-1]
print()
print('last key:', repr(last_key))
# find where last key value ends
print('=== DETAILED_SPECS raw tail ===')
print(html[html.find('"'+last_key+'"', start):html.find('"'+last_key+'"', start)+400])
